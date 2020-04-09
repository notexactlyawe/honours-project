import sys
import time
import sqlite3
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

MAX_CONCURRENT = 10

def generate_tstamps(first_downscale, period):
    return [first_downscale + period*60*i
            for i in range(MAX_CONCURRENT)]

def fetch_data(db_filename):
    db = sqlite3.connect(db_filename)
    c = db.execute('SELECT time FROM heartbeat WHERE type!="executing"')
    times = c.fetchall()
    return times

def group_data(data, tstamps):
    print(tstamps)
    print(data[-1])
    groups = [list() for i in range(len(tstamps))]
    curr_idx = 0
    for time in data:
        t = float(time[0])
        if t > tstamps[curr_idx]:
            curr_idx += 1
        groups[curr_idx].append(t)
    assert(len(data) == sum([len(i) for i in groups]))
    return groups

def create_diff_arr(orig_arr):
    diff_arr = []
    for i in range(1, len(orig_arr)):
        diff_arr.append(orig_arr[i] - orig_arr[i-1])
    return diff_arr

if __name__ == "__main__":
    db_filename = sys.argv[1]
    # ISO format in local time of first downscale event
    first_downscale = time.mktime(datetime.fromisoformat(sys.argv[2]).timetuple())
    period = int(sys.argv[3])
    tstamps = generate_tstamps(first_downscale, period)
    times = fetch_data(db_filename)
    groups = group_data(times, tstamps)
    diffs = [create_diff_arr(a) for a in groups]
    means = []
    std = []
    idx = 10
    for a in diffs:
        means.append(np.mean(a))
        std.append(np.std(a))
        print(idx, means[-1], std[-1], len(a))
        idx -= 1
    print(np.corrcoef(range(1, 11), means[::-1]))
    plt.plot(range(1, 11), means[::-1])
    plt.plot(range(1, 11), std[::-1])
    plt.show()
