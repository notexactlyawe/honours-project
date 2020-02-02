import time

# record time early as possible
t = time.time()

import requests
import os
import sys
import signal

HEARTBEAT_PERIOD = 3 #s

host = os.environ['METRICS_SERVICE_HOST']
port = os.environ['METRICS_SERVICE_PORT']

startup_url = f"http://{host}:{port}/startup"
heartbeat_url = f"http://{host}:{port}/heartbeat"
death_url = f"http://{host}:{port}/death"

r = requests.post(startup_url, data={"start": t})
id_ = r.text

def busy_wait(sleep_time, perc_cpu):
    # idea is that time.sleep() will not use CPU but busy wait will
    finish_time = time.time() + sleep_time
    time.sleep(sleep_time * (1 - perc_cpu))
    while (time.time() < finish_time):
        pass

def exit_handler(signum, frame):
    t = time.time()
    requests.post(death_url, data={"id": id_, "death": t})
    sys.exit()

signal.signal(signal.SIGTERM, exit_handler)
signal.signal(signal.SIGINT, exit_handler)

while True:
    r = requests.post(heartbeat_url, data={"id": id_})
    perc_cpu = float(r.text)
    busy_wait(HEARTBEAT_PERIOD, perc_cpu)
