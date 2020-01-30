import time

# record time early as possible
t = time.time()

import requests
import os

HEARTBEAT_PERIOD = 3 #s

host = os.environ['METRICS_SERVICE_HOST']
port = os.environ['METRICS_SERVICE_PORT']

startup_url = f"http://{host}:{port}/startup"
heartbeat_url = f"http://{host}:{port}/heartbeat"

r = requests.post(startup_url, data={"start": t})
id_ = r.text

# mvp is that the application changes every 15 seconds between high CPU usage and low CPU usage
# probably need a function busy_wait(time, percent) that will wait for time using percent of the CPU
# Every few seconds we send a heartbeat message to the server and it tells us what percent to run at

def busy_wait(sleep_time, perc_cpu):
    # idea is that time.sleep() will not use CPU but busy wait will
    finish_time = time.time() + sleep_time
    time.sleep(sleep_time * (1 - perc_cpu))
    while (time.time() < finish_time):
        pass

while True:
    r = requests.post(heartbeat_url, data={"id": id_})
    perc_cpu = float(r.text)
    busy_wait(HEARTBEAT_PERIOD, perc_cpu)
