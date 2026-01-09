FROM ghcr.io/synerbi/sirf:petric2

USER root
RUN mamba install -c conda-forge array-api-compat cupy cuda-version=12.9
RUN pip install git+https://github.com/TomographicImaging/Hackathon-000-Stochastic-QualityMetrics.git

ARG GROUP_ID
# RUN groupadd -g 27 outworld 
RUN usermod -aG ${GROUP_ID} jovyan

USER jovyan