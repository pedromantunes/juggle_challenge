# base image
FROM python:3

# The enviroment variable ensures that the python output is set straight
# to the terminal with out buffering it first
ENV PYTHONBUFFERED 1

#directory to store app source code
RUN mkdir /juggle_challenge

#switch to /app directory so that everything runs from here
WORKDIR /juggle_challenge

#copy the app code to image working directory
COPY ./juggle_challenge /juggle_challenge

#let pip install required packages
RUN pip install -r requirements.txt