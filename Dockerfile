###################################################
# STAGE: alias docker images
###################################################
FROM ubuntu:18.04 as base-sys

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Shanghai
ARG PYTHON_VERSION=3.8

FROM base-sys as base
#FROM redis:6.2.6
#COPY ./redis.conf /data/
#CMD redis-server /data/redis.conf

RUN apt update && apt install -y build-essential netcat
RUN apt install -y vim procps wget curl tar ca-certificates git-all ssh build-essential g++ gcc libsndfile1
RUN apt install -y gfortran make cmake automake autoconf libtool pkg-config xz-utils
RUN rm -rf /var/lib/apt/lists/*


# conda
COPY ./deploy/ /app/deploy/

RUN curl -k -o ~/miniconda.sh https://repo.anaconda.com/miniconda/Miniconda3-py37_4.9.2-Linux-x86_64.sh && \
    chmod +x ~/miniconda.sh && ~/miniconda.sh -b -p /opt/conda && rm -f ~/miniconda.sh

RUN mkdir -p $HOME/.pip && bash -c "cp -v /app/deploy/pip.conf $HOME/.pip/"
RUN bash -c 'export PATH="/opt/conda/bin:$HOME/.local/bin:$PATH" && conda init bash && source ~/.bashrc && pip install conda-pack && python -V'
ENV PATH="/opt/conda/bin:${PATH}"


###################################################
# STAGE: ci
###################################################
FROM base as ci
ENV LANG C.UTF-8
WORKDIR /app/
COPY ./requirements/ /app/requirements/
RUN bash -c 'pip install --upgrade pip'
RUN bash -c 'pip install -r requirements/service.txt --no-cache-dir' #service.txt

###################################################
# STAGE: service: default uvicorn backend
###################################################
FROM ci as service

COPY . /app

ENV PYTHONUNBUFFERED 1
EXPOSE 8080
ENV PYTHONPATH=/app
CMD uvicorn --host=127.0.0.1 task-idrun:app --workers=2

###################################################
# STAGE: aicloud
###################################################
WORKDIR /usr/local/tfs-publish
FROM service as deploy-aicloud
LABEL source="TITAN"
RUN chmod +x /app/*.sh
RUN mkdir -p /usr/local/tfs-publish /var/log/tfs-publish
RUN mv /app/* /usr/local/tfs-publish/

# ###################################################
# # STAGE: yunxiao
# ###################################################
FROM service as deploy-yunxiao

LABEL source="TITAN"
RUN echo "PATH:${PATH}"
WORKDIR /app
RUN chmod +x /app/*.sh
CMD bash -c './run.sh start'

# COPY pack.sh /app
# RUN echo "PATH:${PATH}"
# WORKDIR /app

# LABEL source="TITAN"
# RUN cp -r /etc/skel /home/jenkins && \
#   chown -R jenkins:jenkins /home/jenkins && \
#   mkdir -p /build/release && chown -Rv jenkins:jenkins /build/release && \
#   chmod +x /app/hifactory/run.sh && chown -R jenkins:jenkins /app
# #USER jenkins

###################################################
# STAGE: default
###################################################
# ßFROM service AS deploy-service
