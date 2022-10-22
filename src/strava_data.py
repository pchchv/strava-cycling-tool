"""
Getting data from Strava API
"""

import requests


def get_timeinterval_activity_data(access_token: str, before: int, after: int) -> list:
    """
    @params:
        before, after - should be in UNIX time format
    """
    page_id = 1
    per_page = 50
    my_dataset = []
    while True:
        try:
            base_url = "https://www.strava.com/api/v3/athlete/activities"
            header = {'Authorization': 'Bearer ' + access_token}
            param = {
				'before': before,
				'after': after,
				'per_page': per_page,
				'page': page_id
			}
            r = requests.get(base_url, headers=header, params=param)
        except requests.exceptions.RequestException:
            return None  
        dataset = r.json()
        if not dataset:
            break
        page_id += 1
        my_dataset += dataset
    return my_dataset
