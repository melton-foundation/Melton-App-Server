FROM python:3.6-slim

RUN apt-get update && apt-get install
RUN apt-get install -y build-essential
RUN apt-get -y install python3-dev
RUN apt-get install -y libpq-dev
RUN mkdir /code
ADD . /code
WORKDIR /code
RUN pip install -r requirements.txt
WORKDIR /code/api
EXPOSE 8000
CMD ["sh", "-c", "python manage.py collectstatic --noinput && python manage.py migrate && gunicorn api.wsgi --bind 0.0.0.0:8000"]
