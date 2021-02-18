"""

@author: Jesper Kristensen
Iterate Labs, Inc. All Rights Reserved, Patent Pending
"""

from app.tasks import run_status

# Jessie: Deactivate this test since we are not using Athena anymore
def __test_status_endpoint():

    response = run_status()

    assert response["status_code"] == 200
