from datetime import datetime
from flask import Flask, request, render_template

app = Flask(__name__)
heartbeats = []
startup_times = []

@app.route('/')
def index():
    if len(startup_times) == 0:
        return "No startups yet"
    avg_time = sum(startup_times) / len(startup_times)
    last_seen = datetime.fromtimestamp(heartbeats[-1])
    return render_template(
        'index.html', startup_times=startup_times, avg_time=avg_time, last_seen=last_seen
    )

@app.route('/collect', methods=['POST'])
def collect():
    print(request.form)
    heartbeats.append(float(request.form['start']))
    if len(heartbeats) > 1:
        startup_times.append(heartbeats[-1] - heartbeats[-2])
    return "OK"
