FROM python:3.7

RUN mkdir /IE
WORKDIR /IE
ADD . /IE/

ENV PYTHONUNBUFFERED 1
ENV LANG C.UTF-8
ENV DEBIAN_FRONTEND=noninteractive

ENV PORT=8000

RUN sed -i -e "s/'NAME': ''/'NAME': 'ie'/g" ./src/ie_django/settings.py
RUN sed -i -e "s/'USER': ''/'USER': 'root'/g" ./src/ie_django/settings.py
RUN sed -i -e "s/'PASSWORD': ''/'PASSWORD': 'root'/g" ./src/ie_django/settings.py
RUN sed -i -e "s/'HOST': 'localhost'/'HOST': 'db'/g" ./src/ie_django/settings.py
RUN apt-get update
RUN apt-get install --yes --no-install-recommends apt-utils
RUN pip install --upgrade pip
RUN apt-get -q update && apt-get -qy install netcat
RUN pip install -r requirements.txt
RUN python ./src/manage.py collectstatic

ENV WAIT_VERSION 2.7.2
ADD https://github.com/ufoscout/docker-compose-wait/releases/download/$WAIT_VERSION/wait /wait
# https://github.com/ufoscout/docker-compose-wait/blob/master/LICENSE
RUN chmod +x /wait

EXPOSE 8000
