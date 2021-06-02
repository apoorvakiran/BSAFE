FROM python:3.8.10-slim-buster

WORKDIR /usr/src/app

RUN apt-get update 
RUN apt-get install -y ruby-full git

RUN gem install foreman

RUN pip3 install pipenv

ADD . /usr/src/app
#RUN pipenv install --dev
#RUN pipenv run python -m pytest -v -n32 tests/

RUN pipenv install --deploy

CMD foreman s
