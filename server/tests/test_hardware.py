import pytest

import app as server


@pytest.fixture
def project(jane):
    server.seed_hardware_sets()
    jane.post("/create_project", json={"projectName": "Project One", "projectId": "proj1"})
    return "proj1"


def availability(c, hw_set):
    return c.post("/get_hw_info", json={"hwSetName": hw_set}).get_json()["availability"]


def checked_out(c, hw_set, project_id="proj1"):
    project = c.post("/get_project_info", json={"projectId": project_id}).get_json()["project"]
    return project["hwSets"].get(hw_set, 0)


def check_out(c, hw_set, qty, project_id="proj1"):
    return c.post("/check_out", json={"projectId": project_id, "hwSetName": hw_set, "qty": qty})


def check_in(c, hw_set, qty, project_id="proj1"):
    return c.post("/check_in", json={"projectId": project_id, "hwSetName": hw_set, "qty": qty})


@pytest.mark.parametrize("hw_set", ["HWSet1", "HWSet2"])
def test_check_out_reduces_availability(jane, project, hw_set):
    res = check_out(jane, hw_set, 25)

    assert res.status_code == 200
    assert res.get_json()["availability"] == 75
    assert availability(jane, hw_set) == 75
    assert checked_out(jane, hw_set) == 25


def test_check_out_more_than_available(jane, project):
    check_out(jane, "HWSet1", 60)
    res = check_out(jane, "HWSet1", 41)

    assert res.status_code == 400
    assert availability(jane, "HWSet1") == 40
    assert checked_out(jane, "HWSet1") == 60


def test_check_in_increases_availability(jane, project):
    check_out(jane, "HWSet1", 30)
    res = check_in(jane, "HWSet1", 10)

    assert res.status_code == 200
    assert availability(jane, "HWSet1") == 80
    assert checked_out(jane, "HWSet1") == 20


def test_state_persists_after_logging_out(jane, project):
    check_out(jane, "HWSet1", 15)
    jane.post("/logout")
    assert check_out(jane, "HWSet1", 1).status_code == 401

    jane.post("/login", json={"userId": "jane123", "password": "secret"})
    assert availability(jane, "HWSet1") == 85
    assert checked_out(jane, "HWSet1") == 15


def test_non_member_cannot_check_out_or_in(jane, bob, project):
    check_out(jane, "HWSet1", 10)

    assert check_out(bob, "HWSet1", 5).status_code == 400
    assert check_in(bob, "HWSet1", 5).status_code == 400
    assert availability(jane, "HWSet1") == 90
    assert checked_out(jane, "HWSet1") == 10


def test_member_can_check_in_units_another_member_took(jane, bob, project):
    check_out(jane, "HWSet2", 20)
    bob.post("/join_project", json={"projectId": project})
    res = check_in(bob, "HWSet2", 20)

    assert res.status_code == 200
    assert availability(bob, "HWSet2") == 100
    assert checked_out(bob, "HWSet2") == 0
