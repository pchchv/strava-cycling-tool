"""
Project that uses the Strava API to download and analyze cycling training data
"""

from strava_upload import preprocessing
from fit_file_tools import fix_fit_activity_files

def main():
    """
    The main function that starts the application
    """
    preprocessing()
    fix_fit_activity_files()


if __name__ == "__main__":
    main()
