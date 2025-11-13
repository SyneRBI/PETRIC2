#
# SPDX-License-Identifier: Apache-2.0
#
# Class implementing the LBFGSB-PC algorithm in sirf.STIR
#
# Authors:  Kris Thielemans
#
# Based on Georg Schramm's
# https://github.com/SyneRBI/PETRIC-MaGeZ/blob/a690205b2e3ec874e621ed2a32a802cd0bed4c1d/simulation_src/sim_stochastic_grad.py
# but with using diag(H.1) as preconditioner at the moment, as per Tsai's paper (see ref in the class doc)
#
# Copyright 2025 University College London

import numpy as np
import numpy.typing as npt
import sirf.STIR as STIR
from scipy.optimize import fmin_l_bfgs_b
from pathlib import Path


class LBFGSBPC:
    """Implementation of the LBFGSB-PC Algorithm

    See
    Tsai et al,
    Fast Quasi-Newton Algorithms for Penalized Reconstruction in Emission Tomography and Further Improvements via Preconditioning
    IEEE TRANSACTIONS ON MEDICAL IMAGING, VOL. 37, NO. 4, APRIL 2018
    DOI: 10.1109/TMI.2017.2786865

    WARNING: it maximises the objective function (as required by sirf.STIR.ObjectiveFunction).
    WARNING: the implementation uses asarray(), which means you need SIRF 3.9. You should be able to just replace it with as_array() otherwise.

    This implementation is NOT a CIL.Algorithm, but it behaves somewhat as one.
    """

    def __init__(
        self,
        objfun: STIR.ObjectiveFunction,
        initial: STIR.ImageData,
        update_objective_interval: int = 0,
        write_at_interval: bool = True,
        outdir: Path = Path('.'),
    ):
        self.trunc_filter = STIR.TruncateToCylinderProcessor()
        self.objfun = objfun
        self.initial = initial.clone()
        self.trunc_filter.apply(self.initial)
        self.shape = initial.shape
        self.output = None
        self.update_objective_interval = update_objective_interval
        self.write_at_interval = write_at_interval
        self.outdir = outdir
        precon = objfun.multiply_with_Hessian(initial, initial.get_uniform_copy(1)) * -1
        self.Dinv_SIRF = precon.maximum(1).power(-0.5)
        self.trunc_filter.apply(self.Dinv_SIRF)
        self.Dinv = self.Dinv_SIRF.asarray().ravel()
        # self.Dinv_SIRF.show(title='Dinv')
        self.tmp_for_value = initial.clone()
        self.tmp_for_gradient = initial.clone()

    def precond_objfun_value(self, z: npt.ArrayLike) -> float:
        self.tmp_for_value.fill(np.reshape(z * self.Dinv, self.shape))
        return -self.objfun(self.tmp_for_value)

    def precond_objfun_gradient(self, z: npt.ArrayLike) -> np.ndarray:
        self.tmp_for_gradient.fill(np.reshape(z * self.Dinv, self.shape))
        return (
            self.objfun.gradient(self.tmp_for_gradient).asarray().ravel()
            * self.Dinv
            * -1
        )

    def callback(self, x):
        if (
            self.update_objective_interval > 0
            and self.iter % self.update_objective_interval == 0
        ):
            self.loss.append(-self.precond_objfun_value(x))
            self.iterations.append(self.iter)
            if self.write_at_interval and self.iter > 0:
                print ("Iteration", self.iter, "objective:", self.loss[-1])
                res = self.tmp_for_value.get_uniform_copy(0)
                xx = np.reshape(x[0] * self.Dinv, self.shape)
                np.save(self.outdir / f"LBFGSBPC_iter{self.iter:04d}.npy", xx)
                res.fill(xx)
                res.write(str(self.outdir / f"LBFGSBPC_iter{self.iter:04d}.hv"))
                print(f"Wrote {self.outdir / f'LBFGSBPC_iter{self.iter:04d}.hv'}")
        self.iter += 1

    def process(self, iterations=None) -> None:
        if iterations is None:
            raise ValueError("`missing argument `iterations`")
        precond_init = self.initial / self.Dinv_SIRF
        self.trunc_filter.apply(precond_init)
        precond_init = precond_init.asarray().ravel()
        bounds = precond_init.size * [(0, None)]
        self.iter = 0
        self.loss = []
        self.iterations = []
        # TODO not really required, but it differs from the first value reported by fmin_l_bfgs_b. Not sure why...
        self.callback(precond_init)
        self.iter = 0  # set back again
        res = fmin_l_bfgs_b(
            self.precond_objfun_value,
            precond_init,
            self.precond_objfun_gradient,
            maxiter=iterations,
            bounds=bounds,
            m=20,
            callback=self.callback,
            factr=0,
            pgtol=0,
        )
        # store result (use name "x" for CIL compatibility)
        self.x = self.tmp_for_value.get_uniform_copy(0)
        self.x.fill(np.reshape(res[0] * self.Dinv, self.shape))
        # self.x.fill(np.reshape(res[0], self.shape))
        # self.x.show(title='final image in preconditioned space')
        # self.x *= self.Dinv_SIRF

    def run(
        self, **kwargs
    ) -> None:  # CIL alias, would need to callback and verbose keywords etc
        self.process(**kwargs)

    def get_output(self) -> STIR.ImageData:
        return self.x
