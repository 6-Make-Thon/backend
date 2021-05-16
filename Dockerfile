# set base image (host OS)
#FROM python:3.9
FROM ubuntu:18.04

# set the working directory in the container
WORKDIR /code

ENV DEBIAN_FRONTEND=noninteractive

RUN apt update && apt install -y python3-numpy python3-scipy python3-matplotlib ipython3 python3-pandas python3-sympy python3-nose python3-shapely python3-pip && apt clean

# copy the dependencies file to the working directory
COPY requirements.txt .


# install dependencies
RUN pip3 install -r requirements.txt

# copy the content of the local src directory to the working directory
COPY / .

COPY docker_entrypoint.sh /

RUN chmod a+x /docker_entrypoint.sh

ENTRYPOINT ["/docker_entrypoint.sh"]
