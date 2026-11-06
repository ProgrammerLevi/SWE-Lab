def create_project(c, project_id="proj1", name="Project One"):
    return c.post("/create_project", json={
        "projectName": name, "projectId": project_id, "description": "test project",
    })


def get_projects(c):
    return c.post("/get_user_projects").get_json()


def test_create_project(jane):
    res = create_project(jane)

    assert res.status_code == 201
    owned = get_projects(jane)["owned"]
    assert [p["projectId"] for p in owned] == ["proj1"]
    assert owned[0]["ownerName"] == "Jane"


def test_duplicate_project_id_rejected(jane):
    create_project(jane)
    res = create_project(jane, name="Something else")

    assert res.status_code == 409
    assert len(get_projects(jane)["owned"]) == 1


def test_other_user_cannot_reuse_project_id(jane, bob):
    create_project(jane)
    res = create_project(bob)

    assert res.status_code == 409
    assert get_projects(bob)["owned"] == []


def test_join_project(jane, bob):
    create_project(jane)
    res = bob.post("/join_project", json={"projectId": "proj1"})

    assert res.status_code == 200
    shared = get_projects(bob)["shared"]
    assert [p["projectId"] for p in shared] == ["proj1"]
    assert shared[0]["ownerName"] == "Jane"
    assert len(shared[0]["users"]) == 2


def test_non_member_cannot_view_project(jane, bob):
    create_project(jane)

    res = bob.post("/get_project_info", json={"projectId": "proj1"})
    assert res.status_code == 403

    bob.post("/join_project", json={"projectId": "proj1"})
    res = bob.post("/get_project_info", json={"projectId": "proj1"})
    assert res.status_code == 200
    assert res.get_json()["project"]["projectName"] == "Project One"
