#FROM python:3.9-slim
FROM python:3.7-slim
WORKDIR /usr/src/app

RUN apt-get update 
RUN apt-get install -y ruby-full git

RUN gem install foreman

RUN pip3 install pipenv

ADD Pipfile /usr/src/app/
ADD Pipfile.lock /usr/src/app/
#RUN pipenv --rm
# RUN pipenv lock
# RUN pipenv install
# RUN pipenv sync
# RUN  pipenv  install s3fs
RUN  pipenv install --ignore-pipfile
ADD . /usr/src/app/
#RUN pipenv run python -m pytest -v -n32 tests/
# 
#RUN pipenv install --deploy
#CMD foreman s

CMD ls /usr/src/app;bash /usr/src/app/run-bsafe.sh
