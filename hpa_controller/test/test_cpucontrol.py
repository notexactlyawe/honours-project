import os
import time
import pytest

os.environ["K8S_CPU_TARGET"] = "0.3"

from hpa_controller.metric_server import app

@pytest.fixture
def client():
    app.recreate_db()
    with app.app.test_client() as client:
        yield client

def test_one_worker(client):
    rv = client.post('/startup', data={"start": time.time()})
    assert rv.status_code == 200
    id_ = rv.get_data(as_text=True)
    rv = client.post('/heartbeat', data={"id": id_})
    # high target since less than max pods
    assert rv.get_data(as_text=True) == str(app.HIGH_TARGET)

def test_two_workers(client):
    # create two workers
    rv = client.post('/startup', data={"start": time.time()})
    assert rv.status_code == 200
    id1 = rv.get_data(as_text=True)

    rv = client.post('/startup', data={"start": time.time()})
    assert rv.status_code == 200
    id2 = rv.get_data(as_text=True)

    # low target for both
    rv = client.post('/heartbeat', data={"id": id1})
    assert rv.get_data(as_text=True) == str(app.LOW_TARGET)
    rv = client.post('/heartbeat', data={"id": id2})
    assert rv.get_data(as_text=True) == str(app.LOW_TARGET)

def test_low_high_low(client):
    # create one worker
    rv = client.post('/startup', data={"start": time.time()})
    assert rv.status_code == 200
    id1 = rv.get_data(as_text=True)

    # assert high target
    rv = client.post('/heartbeat', data={"id": id1})
    assert rv.get_data(as_text=True) == str(app.HIGH_TARGET)

    # create second worker
    rv = client.post('/startup', data={"start": time.time()})
    assert rv.status_code == 200
    id2 = rv.get_data(as_text=True)

    # assert low target for both
    rv = client.post('/heartbeat', data={"id": id1})
    assert rv.get_data(as_text=True) == str(app.LOW_TARGET)
    rv = client.post('/heartbeat', data={"id": id2})
    assert rv.get_data(as_text=True) == str(app.LOW_TARGET)

    # destroy worker
    rv = client.post('/death', data={
        "id": id2,
        "death": time.time()
    })
    assert rv.status_code == 200

    # assert high target for surviving worker
    rv = client.post('/heartbeat', data={"id": id1})
    assert rv.get_data(as_text=True) == str(app.HIGH_TARGET)
