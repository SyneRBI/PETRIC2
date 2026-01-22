"""Search beta values
Usage:
  run_beta_search.py <data_set> [options]

Arguments:
  <data_set>      path to data files as well as prefix to use (e.g. Siemens_mMR_NEMA_IQ)
Options:
  --betas=<b>     csv penalisation factors [default: 1,0.1]
  --updates=<u>   number of updates to run [default: 500]
  --interval=<i>  interval to save [default: 2147483647]
"""
__version__ = '0.3.0'

from textwrap import dedent

import matplotlib.pyplot as plt
import numpy as np
from brainweb import volshow
from docopt import docopt

from petric import OUTDIR, SRCDIR, STIR, Algorithm, SaveIters, cil_callbacks, get_data, logging
from sirf.contrib import MaGeZ
from SIRF_data_preparation import data_QC
from SIRF_data_preparation.dataset_settings import get_settings, preferred_scaling


def run(argv=None, Submission=MaGeZ.ALG1, submission_callbacks=[]): # noqa: B006
    assert issubclass(Submission, Algorithm)
    args = docopt(__doc__, argv=argv, version=__version__)
    scanID = args['<data_set>']
    iters = int(args['--updates'])
    interval = int(args['--interval'])
    betas = list(map(float, args['--betas'].split(','))) if args['--betas'] else []

    srcdir = SRCDIR / scanID
    outdir = OUTDIR / scanID
    settings = get_settings(scanID)
    sfs = preferred_scaling[scanID]
    data = get_data(srcdir=srcdir, outdir=outdir)
    petric1_beta = data.prior.get_penalisation_factor()

    for beta in betas:
        outdir_b = outdir / str(beta)
        data.prior.set_penalisation_factor(beta * petric1_beta)
        print(
            dedent(f"""\
            iters: {iters}
            srcdir: {srcdir}
            outdir: {outdir_b}
            interval: {interval}
            penalisation factor:
            - original: {petric1_beta}
            - beta multiplier: {beta}
            - rescaled: {data.prior.get_penalisation_factor()}
            """), flush=True)
        algo = Submission(data, update_objective_interval=interval)
        algo.run(
            iters, callbacks=[SaveIters(outdir_b, interval=interval),
                              cil_callbacks.ProgressCallback()] + submission_callbacks)

        fig = plt.figure()
        data_QC.plot_image(algo.get_output(), **settings.slices)
        fig.suptitle(rf"{scanID} iters={iters} $\beta$={beta} preferred_scaling={sfs}")
        fig.tight_layout(h_pad=0, w_pad=0)
        fig.savefig(outdir / f"slices_{beta}.png")

    i = settings.slices.get('transverse_slice',
                            STIR.ImageData(str(next(outdir.glob("*/iter_final.hv")))).dimensions()[0] // 2)
    volumes = {
        f"$\\beta={f.parent.name}$": np.trim_zeros(STIR.ImageData(str(f)).as_array()[i:i + 1])
        for f in sorted(outdir.glob("*/iter_final.hv"))}
    N = len(volumes)
    volshow(volumes, vmaxs=[settings.vmax] * N, vmins=[0] * N, cmaps=['magma'] * N)
    plt.suptitle(rf"{scanID} iters={iters} preferred_scaling={sfs}")
    plt.tight_layout(h_pad=0, w_pad=0)
    plt.savefig(outdir / "slices.png")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run()
