"""

@author: Jesper Kristensen
Iterate Labs, Inc. All Rights Reserved, Patent Pending
"""

from app.tasks import run_status


def test_status_endpoint():

    return_code = run_status()

    assert return_code == 200
