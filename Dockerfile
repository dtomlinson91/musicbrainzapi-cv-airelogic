FROM python:3.7.6-slim-buster

RUN mkdir /outputs && mkdir /inputs

COPY ./setup.py /inputs/setup.py
COPY ./src /inputs/src

WORKDIR /inputs
RUN python ./setup.py install
