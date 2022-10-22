"""
Pandas will be the backbone of our data manipulation.
"""

import pandas as pd


def create_activity_dataframe(activity_data: list, filters=None) -> pd.DataFrame:
    """
    Analyzing the data from Stava
    """
    activity_dataframe = pd.DataFrame(activity_data, columns=filters)
    return activity_dataframe
