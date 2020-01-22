import time

# record time early as possible
t = time.time()

import requests
import os

host = os.environ['METRICS_SERVICE_HOST']
port = os.environ['METRICS_SERVICE_PORT']

url = f"http://{host}:{port}/collect"

requests.post(url, data={"start": t})

raise Exception("muahahahaha")
