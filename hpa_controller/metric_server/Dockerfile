FROM python:3.8-buster
COPY . /data
WORKDIR /data
RUN pip install -r requirements.txt
ENV FLASK_ENV development
ENV K8S_CPU_TARGET "0.3"
CMD flask run --host=0.0.0.0
