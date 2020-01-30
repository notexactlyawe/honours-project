FROM python:3.8-buster
COPY . /data
WORKDIR /data
RUN pip install -r requirements.txt
ENV SERVER http://127.0.0.1:8080
CMD python worker.py $SERVER
