"""
Getting data from Strava API
"""

import requests


def get_athlete(access_token: str) -> dict:
    """
    @params
        access_token
    """
    try:
        base_url = "https://www.strava.com/api/v3/athlete"
        header = {'Authorization': 'Bearer ' + access_token}
        res = requests.get(base_url, headers=header)
    except requests.exceptions.RequestException:
        return None
    return res.json()


def get_recent_ride_totals(athlete_id: int, access_token: str) -> dict:
    """
    @params:
        athlete_id
        access_token
    """
    try:
        base_url = "https://www.strava.com/api/v3/athletes/{}/stats".format(athlete_id)
        header = {'Authorization': 'Bearer ' + access_token}
        res = requests.get(base_url, headers=header)
    except requests.exceptions.RequestException:
        return None
    return res.json().get('recent_ride_totals')


def get_latest_activity_data(access_token: str, number_of_activities: int = 1) -> list:
    """
    @params:
        number_of_activities
    """
    try:
        base_url = "https://www.strava.com/api/v3/athlete/activities"
        header = {'Authorization': 'Bearer ' + access_token}
        param = {
			'per_page': number_of_activities,
			'page': 1
		}
        r = requests.get(base_url, headers=header, params=param)
    except requests.exceptions.RequestException:
        return None

    my_dataset = r.json()

    return my_dataset


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


def get_all_activity_data(access_token: str) -> list:
    """
    @params:
        access_token
    """
    page_id = 1
    per_page = 50
    my_dataset = []
    while True:
        try:
            base_url = "https://www.strava.com/api/v3/athlete/activities"
            header = {'Authorization': 'Bearer ' + access_token}
            param = {
				'per_page': per_page,
				'page': page_id
			}
            res = requests.get(base_url, headers=header, params=param)
        except requests.exceptions.RequestException:
            return None
        dataset = res.json()
        if not dataset:
            break
        page_id += 1
        my_dataset += dataset
    return my_dataset
