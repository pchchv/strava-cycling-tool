"""
Project that uses the Strava API to download and analyze cycling training data
"""

from strava_upload import preprocessing, upload_fit_activity_files
from fit_file_tools import fix_fit_activity_files
from auth import get_access_token

def main():
    """
    The main function that starts the application
    """
    preprocessing()
    fix_fit_activity_files()
    upload_fit_activity_files(get_access_token())


if __name__ == "__main__":
    main()
