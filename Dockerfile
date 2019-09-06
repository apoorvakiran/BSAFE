FROM python:3.7-slim

WORKDIR /usr/src/app

RUN apt-get update && apt-get install -y ruby-full

RUN gem install foreman

RUN pip3 install pipenv
                                           
ADD . /usr/src/app

RUN pipenv install --deploy

CMD foreman s





