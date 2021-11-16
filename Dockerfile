FROM python:3.6-slim-buster

RUN mkdir -p /home/app

ENV HOME=/home/app
ENV APP_HOME=/home/app/web
RUN mkdir $APP_HOME
WORKDIR $APP_HOME

RUN addgroup --system flask_app && adduser --system --group flask_user

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y netcat


RUN pip install --upgrade pip
COPY ./requirements.dev.txt $APP_HOME/requirements.txt
RUN pip install -r requirements.txt

COPY ./entrypoint.sh $APP_HOME

COPY . $APP_HOME

RUN chown -R flask_user:flask_app $APP_HOME

USER flask_user

ENTRYPOINT ["/home/app/web/entrypoint.sh"]