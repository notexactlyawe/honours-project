import os
import time
import sqlite3
from flask import Flask, request, render_template, g

app = Flask(__name__)

DATABASE = 'temp.db'

# Target CPU percentage as a float 0-1
K8S_CPU_TARGET = float(os.environ['K8S_CPU_TARGET'])
# let's assume a flip-flop between them for now
MIN_PODS = 1
MAX_PODS = 2

# halfway between the target and 0 CPU
LOW_TARGET = K8S_CPU_TARGET / 2
# halfway between the target and 100 CPU
HIGH_TARGET = (1 + K8S_CPU_TARGET) / 2

def recreate_db():
    try:
        os.remove(DATABASE)
    except:
        print("Couldn't remove database")
    db = sqlite3.connect(DATABASE)
    c = db.cursor()
    c.execute('''CREATE TABLE heartbeat (pod int, time text, type text)''')
    c.execute('''CREATE TABLE pods (pod int, active bool)''')
    db.commit()
    db.close()

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.route('/')
def index():
    db = get_db()
    # get last 10 cycles
    c = db.execute('''SELECT time FROM heartbeat WHERE type!="executing" LIMIT 11''')
    times = c.fetchall()
    if len(times) > 1:
        times_with_diff = [
            (times[i][0], float(times[i][0]) - float(times[i-1][0]))
            for i in range(1, len(times))
        ]
        return render_template("index.html", times=times_with_diff)
    return f"No startups/deaths yet"

@app.route('/startup', methods=['POST'])
def startup():
    db = get_db()
    c = db.execute("SELECT pod FROM pods ORDER BY pod DESC")
    if (row := c.fetchone()) is not None:
        id_ = row[0] + 1
    else:
        id_ = 0
    startup_time = request.form['start']
    c.execute('''INSERT INTO pods VALUES (?, 1)''', (id_,))
    c.execute('''INSERT INTO heartbeat VALUES (?, ?, "startup")''', (id_, startup_time))
    db.commit()
    return str(id_)

@app.route('/death', methods=['POST'])
def death():
    db = get_db()
    id_ = request.form['id']
    t = request.form['death']
    c = db.execute('''UPDATE pods SET active=0 WHERE pod=?''', (id_,))
    c.execute('''INSERT INTO heartbeat VALUES (?, ?, "death")''', (id_, t))
    db.commit()
    return "OK"

@app.route('/heartbeat', methods=['POST'])
def heartbeat():
    db = get_db()
    c = db.execute("SELECT COUNT(pod) FROM pods WHERE active=1")
    active_pods = c.fetchone()[0]
    id_ = request.form['id']
    db.execute('''INSERT INTO heartbeat VALUES (?, ?, "executing")''', (id_, str(time.time())))
    db.commit()
    if active_pods >= MAX_PODS:
        return str(LOW_TARGET)
    return str(HIGH_TARGET)

if __name__ == "__main__":
    recreate_db()
    app.run(debug=True)
