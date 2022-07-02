#########################################
# Dockerfile to build STREAM 
#########################################

# syntax=docker/dockerfile:1
# Set the base image to anaconda3
FROM continuumio/anaconda3
#FROM continuumio/conda-ci-linux-64-python3.7

# File Author / Maintainer
MAINTAINER Wei He

ENV SHELL bash

RUN conda install r-base
RUN conda install -c bioconda viennarna
RUN conda config --add channels defaults
RUN conda config --add channels conda-forge
RUN conda config --add channels bioconda
#RUN conda create -n tensorflow_env tensorflow=2
#RUN conda activate tensorflow_env

#Add build tools
RUN ln -s /bin/tar /bin/gtar
#RUN apt-get update && apt-get install build-essential zlib1g-dev -y

#add Python dependencies
RUN pip install keras
RUN pip install tensorflow
RUN pip install biopython
#RUN conda install -c apple tensorflow-deps
#RUN pip install tensorflow-macos
#RUN pip install tensorflow-metal
#RUN apt-get install unzip libxml2 libxml2-dev -y

COPY ./GuideVar/. /GuideVar
WORKDIR /GuideVar
RUN ls /GuideVar/data
RUN ls /GuideVar/models

ENTRYPOINT ["/opt/conda/bin/python", "/GuideVar/guidevar_entry.py"]



