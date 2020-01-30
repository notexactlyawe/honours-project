import os
import time
import sqlite3
from flask import Flask, request, render_template, g

app = Flask(__name__)

DATABASE = 'temp.db'

# TODO:
# - Write up this design in dissertation
#   - Including assumption of setting minimum decrease in control loop
# - Detect how many pods are alive right now
# - Figure out CPU to send to pods
# - Maybe conduct experiment to prove that the CPU usage works (only proved in top)
#   - This would need to be conducted on a kubernetes cluster with the metrics server on
# - Fill in getting started in readme

def recreate_db():
    try:
        os.remove(DATABASE)
    except:
        pass
    db = sqlite3.connect(DATABASE)
    c = db.cursor()
    c.execute('''CREATE TABLE heartbeat (pod int, time text)''')
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
    c = db.execute("SELECT * FROM heartbeat ORDER BY pod")
    active_pods = c.fetchall()
    print(active_pods)
    return render_template(
        'index.html', active_pods=active_pods
    )

@app.route('/startup', methods=['POST'])
def startup():
    db = get_db()
    c = db.execute("SELECT pod FROM heartbeat ORDER BY pod DESC")
    try:
        id_ = c.fetchone()[0] + 1
    except TypeError:
        print("Assigned ID of 0")
        id_ = 0
    startup_time = request.form['start']
    c.execute("INSERT INTO heartbeat VALUES (?, ?)", (id_, startup_time))
    db.commit()
    return str(id_)

@app.route('/heartbeat', methods=['POST'])
def heartbeat():
    db = get_db()
    id_ = request.form['id']
    db.execute("INSERT INTO heartbeat VALUES (?, ?)", (id_, str(time.time())))
    db.commit()
    return "0.7"

if __name__ == "__main__":
    recreate_db()
    app.run(debug=True)
