FROM python:3.6

RUN mkdir /code
ADD app /code
WORKDIR /code
RUN pip install -r requirements.txt
WORKDIR /code/api
EXPOSE 8000
CMD ["sh", "-c", "python manage.py collectstatic --noinput && gunicorn api.wsgi --bind 0.0.0.0:8000"]
