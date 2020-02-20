import sys
import sqlite3
import matplotlib.pyplot as plt

def read_cycle_times(db_filename):
    db = sqlite3.connect(db_filename)
    c = db.execute('''SELECT time FROM heartbeat WHERE type!="executing";''')
    # list of 1-tuples
    times = c.fetchall()
    exp_start = float(times[0][0])
    x_axis = list(range(1, len(times)))
    y_axis = [float(times[i][0]) - float(times[i-1][0]) for i in range(1, len(times))]
    db.close()
    return x_axis, y_axis

if __name__ == "__main__":
    # python graphit.py some.db
    db_f = sys.argv[1]
    x, y = read_cycle_times(db_f)
    plt.plot(x, y)
    plt.ylabel("Cycle time (s)")
    plt.xlabel("Cycle #")
    plt.title(f"Time taken for HPA controller to affect state of busy_worker. From {db_f}")
    plt.show()
