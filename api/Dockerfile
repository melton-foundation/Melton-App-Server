FROM python:3

RUN mkdir /code
WORKDIR /code

COPY requirements.txt ./
RUN pip install  -r requirements.txt


COPY . .
CMD ls -a
CMD python manage.py runserver 0.0.0.0:8000