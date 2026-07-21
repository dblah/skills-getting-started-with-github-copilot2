from fastapi.testclient import TestClient

from src.app import app, activities


client = TestClient(app)


def test_get_activities_returns_all():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    # Expect at least the seeded activities to be present
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Art Club" in data


def test_signup_adds_participant_and_allows_cleanup():
    activity_name = "Art Club"
    email = "test.signup@mergington.edu"

    # Ensure clean start
    if email in activities[activity_name]["participants"]:
        activities[activity_name]["participants"].remove(email)

    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    assert response.status_code == 200
    assert email in activities[activity_name]["participants"]
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"

    # cleanup
    if email in activities[activity_name]["participants"]:
        activities[activity_name]["participants"].remove(email)


def test_signup_existing_returns_400():
    activity_name = "Chess Club"
    email = "existing.student@mergington.edu"

    # ensure the email is present
    if email not in activities[activity_name]["participants"]:
        activities[activity_name]["participants"].append(email)

    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 400

    # cleanup (leave original state as before test)
    # no change needed because we appended above only if missing


def test_activity_not_found_returns_404_for_signup_and_unregister():
    activity_name = "Nonexistent Club"
    email = "nobody@mergington.edu"

    resp_signup = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert resp_signup.status_code == 404

    resp_unregister = client.delete(f"/activities/{activity_name}/unregister?email={email}")
    assert resp_unregister.status_code == 404
