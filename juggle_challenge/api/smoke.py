from __future__ import annotations

import copy
import random
import requests
import time

from juggle_challenge.rest_api import BearerAuth, Client


api = Client(
    base_url="http://127.0.0.1:8000/",
    exception_raise_enabled=False,
)


def test():
    random.seed(time.time())

    username = "user-" + "".join([str(random.randint(0, 9)) for _ in range(12)])

    # Create user
    create_user_url = "v1/users/"
    user_payload = {
        "first_name": "pedro",
        "last_name": "antunes",
        "username": username,
        "password": "1234",
    }

    # Authentication: unauthorized call
    response = api(create_user_url).post(**user_payload)
    assert response.status_code == requests.codes.created, response.text

    # Authentication: retrieve token
    auth_token_url = "v1/token/"

    authentication_payload = {
        "username": username,
        "password": "1234",
    }

    access_token = api(auth_token_url).post(**authentication_payload).json()["access"]

    api.auth = BearerAuth(access_token)

    # Create business
    business_url = "v1/business/"
    business_payload = {"company_name": "Juggle", "website": "http://www.juggle.uk"}

    response = api(business_url).post(**business_payload)
    assert response.status_code == requests.codes.created, response.text

    business_id = response.json()["business_id"]

    # Create Job
    job_creation_url = f"{business_url}{business_id}/jobs/"
    job_payload = {
        "title": "Fullstack Developer",
        "daily_rate_range": "22.45",
        "availability_ids": ["2"],
        "location_ids": ["1"],
        "skills": ["some skill"],
    }

    response = api(job_creation_url).post(**job_payload)
    assert response.status_code == requests.codes.created, response.text

    job_id = response.json()["job_id"]

    job_serialized = copy.deepcopy(job_payload)

    del job_serialized["availability_ids"]
    del job_serialized["location_ids"]

    job_serialized.update(
        job_id=job_id,
        locations=[{"location_id": "1", "description": "onsite"}],
        daily_rate_range="22.450",
        availabilities=[{"availability_id": "2", "description": "3-4 days/wk"}],
    )

    assert response.json() == job_serialized, job_serialized

    # no applications for a given job yet
    job_url = "v1/jobs/"
    job_professionals_url = f"{job_url}{job_id}/professionals/"

    response = api(job_professionals_url).get()

    assert response.json() == []

    # Create Professional
    professional_url = "v1/professionals/"
    professional_payload = {
        "title": "Eng",
        "full_name": "Pedro Miguel Azevedo Antunes",
        "email": "pedro@pedro.pt",
        "daily_rate_range": "22.45",
        "availability_ids": ["2"],
        "location_ids": ["1"],
    }

    response = api(professional_url).post(**professional_payload)
    assert response.status_code == requests.codes.created, response.text

    professional_id = response.json()["professional_id"]

    professional_serialized = copy.deepcopy(professional_payload)

    del professional_serialized["availability_ids"]
    del professional_serialized["location_ids"]

    professional_serialized.update(
        professional_id=professional_id,
        locations=[{"location_id": "1", "description": "onsite"}],
        daily_rate_range="22.450",
        availabilities=[{"availability_id": "2", "description": "3-4 days/wk"}],
        jobs=[],
    )

    assert response.json() == professional_serialized, professional_serialized

    # Apply to a Job
    job_apply_url = f"{professional_url}{professional_id}/job-apply/{job_id}/"
    response = api(job_apply_url).put()

    # Get Jobs for professionals
    professional_jobs_url = f"{professional_url}{professional_id}/jobs/"
    response = api(professional_jobs_url).get()

    assert response.json() == [job_serialized], job_serialized

    # Get applications for a Job
    job_url = "v1/jobs/"
    job_professionals_url = f"{job_url}{job_id}/professionals/"

    response = api(job_professionals_url).get()

    professional_serialized.update(jobs=[job_serialized])

    assert response.json() == [professional_serialized], professional_serialized

    # Delete Existing professional
    response = api(f"{professional_url}{professional_id}").delete()

    # Check limit of applications per day
    full_names = ["John 1", "John 2", "James 3", "James 4"]
    for name in full_names:
        professional_payload["full_name"] = name
        response = api(professional_url).post(**professional_payload)
        professional_id = response.json()["professional_id"]

        # Apply to same job
        job_apply_url = f"{professional_url}{professional_id}/job-apply/{job_id}/"
        api(job_apply_url).put()

    # Check that the job apply limit was reached
    professional_payload["full_name"] = "John Limit"
    response = api(professional_url).post(**professional_payload)
    professional_id = response.json()["professional_id"]

    job_apply_url = f"{professional_url}{professional_id}/job-apply/{job_id}/"
    response = api(job_apply_url).put()

    assert response.json() == [
        "The limit of applications for the current job was reached. Please try again tomorrow."
    ]

    # Filter Professionals by first Name
    professionals_name_filter_url = "v1/professionals/?full_name=John"
    response = api(professionals_name_filter_url).get()


if __name__ == "__main__":
    test()
