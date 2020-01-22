FROM python:3.8-buster
COPY . /data
WORKDIR /data
RUN pip install -r requirements.txt
ENV FLASK_ENV development
CMD flask run --host=0.0.0.0
