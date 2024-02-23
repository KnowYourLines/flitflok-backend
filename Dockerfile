FROM python:3.10.8
ENV PYTHONUNBUFFERED=1
WORKDIR /code
COPY requirements.txt /code/
COPY . /code/
RUN apt update
RUN apt-get -y install binutils libproj-dev gdal-bin
RUN pip install -r requirements.txt