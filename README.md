# PETRIC 2: Second PET Rapid Image reconstruction Challenge

[![website](https://img.shields.io/badge/announcement-website-purple?logo=workplace&logoColor=white)](https://www.ccpsynerbi.ac.uk/events/petric2/)
[![wiki](https://img.shields.io/badge/details-wiki-blue?logo=googledocs&logoColor=white)][wiki]
[![register](https://img.shields.io/badge/participate-register-green?logo=ticktick&logoColor=white)][register]
[![leaderboard](https://img.shields.io/badge/rankings-leaderboard-orange?logo=tensorflow&logoColor=white)][leaderboard]
[![discord](https://img.shields.io/badge/chat-discord-blue?logo=discord&logoColor=white)](https://discord.gg/Ayd72Aa4ry)

## Participating

The organisers will provide GPU-enabled cloud runners which have access to larger private datasets for evaluation. To gain access, you must [register]. The organisers will then create a private team submission repository for you.

[register]: https://github.com/SyneRBI/PETRIC2/issues/new/choose

## What's the same?
As with [the previous challenge (PETRIC1)](https://github.com/SyneRBI/PETRIC), the goal is to solve a maximum a-posteriori (MAP) estimate using a smoothed relative difference prior (RDP), reaching the target image quality as fast as possible.
We provide PET sinogram phantom data from different scanners and private repository on GitHub with an implementation of some reference algorithms.
A live leaderboard which is continuously updated to track your progress.

## What's new?
It's more challenging! The PET sinogram data has fewer counts, meaning algorithms will have to cope with more noise. For more information on the new data, see [wiki/data](https://github.com/SyneRBI/PETRIC2/wiki#data).

In addition to the more challenging data, we have improved our reconstruction software. STIR 6.3 was released which has lots of new features including new analytic reconstruction methods, better GPU support and improved support for reading raw data formats. For more information have a look at the [release notes](https://rawcdn.githack.com/UCL/STIR/c4f12cfc23d5cc85636bc7dedf864ec6c170ec71/documentation/release_6.3.htm). On the SIRF side we focused on speed! We improved the acquisition and image algebra to speed up things by a factor of 3 and optimised our Python interface to ensure we provide data views rather than copying things around. Have a look at the [SIRF 3.9 relase notes](https://github.com/SyneRBI/SIRF/blob/1ba1f9f4f56dfe5ebf1cec5c67d1773056102ae6/CHANGES.md) for more information.

## Timeline
- Start of the challenge: 15 November 2025
- End of the challenge: 15 February 2026

## Awards
The winners of PETRIC2 will be announced as part of the Symposium on AI & Reconstruction for Biomedical Imaging taking place from 9 – 10 March 2026 in London (https://www.ccpsynerbi.ac.uk/events/airbi/). All participants of PETRIC2 will be invited to submit an abstract at the beginning of December 2025 and will then have the opportunity to present their work at the Symposium. More information on the abstract and possible travel stipends will follow soon.

## Layout

The organisers will import your submitted algorithm from `main.py` and then run & evaluate it.
Please create this file! See the example `main_*.py` files for inspiration.

[SIRF](https://github.com/SyneRBI/SIRF), [CIL](https://github.com/TomographicImaging/CIL), and CUDA are already installed (using [synerbi/sirf](https://github.com/synerbi/SIRF-SuperBuild/pkgs/container/sirf)).
Additional dependencies may be specified via `apt.txt`, `environment.yml`, and/or `requirements.txt`.

- (required) `main.py`: must define a `class Submission(cil.optimisation.algorithms.Algorithm)` and a (potentially empty) list of `submission_callbacks`, e.g.:
  + [main_BSREM.py](main_BSREM.py)
  + [main_ISTA.py](main_ISTA.py)
  + [main_OSEM.py](main_OSEM.py)
- `apt.txt`: passed to `apt install`
- `environment.yml`: passed to `conda install`, e.g.:

  ```yml
  name: winning-submission
  channels: [conda-forge, nvidia]
  dependencies:
  - cupy
  - cuda-version 12.8.*
  - pip
  - pip:
    - git+https://github.com/MyResearchGroup/prize-winning-algos
  ```

- `requirements.txt`: passed to `pip install`, e.g.:

  ```txt
  cupy-cuda12x
  git+https://github.com/MyResearchGroup/prize-winning-algos
  ```

> [!TIP]
> You probably should create either an `environment.yml` or `requirements.txt` file (but not both).

You can also find some example notebooks here which should help you with your development:
- https://github.com/SyneRBI/SIRF-Contribs/blob/master/src/notebooks/BSREM_illustration.ipynb

## Organiser Setup

The organisers will execute (after installing [nvidia-docker](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html) & downloading <https://petric.tomography.stfc.ac.uk/2/data/> to `/path/to/data`):

```sh
# 1. git clone & cd to your submission repository
# 2. mount `.` to container `/workdir`:
docker run --rm -it --gpus all -p 6006:6006 \
  -v /path/to/data:/mnt/share/petric:ro \
  -v .:/workdir -w /workdir ghcr.io/synerbi/sirf:petric2 /bin/bash
# 1. optionally, conda/pip/apt install environment.yml/requirements.txt/apt.txt
# 2. run your submission
python petric.py &
# 3. optionally, serve logs at <http://localhost:6006>
tensorboard --bind_all --port 6006 --logdir ./output
```

> [!NOTE]
> [The docker image](https://github.com/SyneRBI/PETRIC-backend/blob/main/Dockerfile) includes Python3.12, SIRF, CIL, [MONAI](https://github.com/Project-MONAI/MONAI), Torch, TensorFlow, and [Stochastic-QualityMetrics](https://github.com/TomographicImaging/Hackathon-000-Stochastic-QualityMetrics).

## FAQ

See the [wiki/Home][wiki] and [wiki/FAQ](https://github.com/SyneRBI/PETRIC2/wiki/FAQ) for more info.

> [!TIP]
> `petric.py` will effectively execute:
>
> ```python
> from main import Submission, submission_callbacks  # your submission (`main.py`)
> from petric import data, metrics  # our data & evaluation
> assert issubclass(Submission, cil.optimisation.algorithms.Algorithm)
> Submission(data).run(numpy.inf, callbacks=submission_callbacks + metrics)
> ```

<!-- br -->

> [!WARNING]
> To avoid timing out (currently 10 min runtime, will likely be increased a bit for the final evaluation after submissions close), please disable any debugging/plotting code before submitting!
> This includes removing any progress/logging from `submission_callbacks` and any debugging from `Submission.__init__`.

- `data` to test/train your `Algorithm`s is available at <https://petric.tomography.stfc.ac.uk/2/data/> and is likely to grow (more info to follow soon)
  + fewer datasets will be available during the submission phase, but more will be available for the final evaluation after submissions close
  + please contact us if you'd like to contribute your own public datasets!
- `metrics` are calculated by `class QualityMetrics` within `petric.py`
  + this does not contribute to your runtime limit
  + effectively, only `Submission(data).run(np.inf, callbacks=submission_callbacks)` is timed
- when using the temporary [leaderboard], it is best to:
  + change `Horizontal Axis` to `Relative`
  + untick `Ignore outliers in chart scaling`
  + see [the wiki](https://github.com/SyneRBI/PETRIC2/wiki#metrics-and-thresholds) for details

Any modifications to `petric.py` are ignored.

[wiki]: https://github.com/SyneRBI/PETRIC2/wiki
[leaderboard]: https://petric.tomography.stfc.ac.uk/2/leaderboard/?smoothing=0#timeseries&_smoothingWeight=0
