"""
Strava Upload Tool
"""

import os
import re
import sys
import imaplib
import subprocess
import glob
import time
import datetime
import email
from typing import Any, Tuple
import requests
from alive_progress import alive_bar
from environment import GMAIL_USER_ID, GMAIL_PASSWORD, ZWIFT_ACTIVITY_DIR, STRAVA_CLIENT_ID
from file_manipulation import move_to_uploaded_or_malformed_activities_folder


def preprocessing():
    """
    Function to prepare .fit file(s) to be uploaded
    """
    process_list = subprocess.Popen('tasklist', stdout=subprocess.PIPE).communicate()[0]
    process_name = "ZwiftApp.exe"
    if process_name.encode() in process_list:
        exit_code = os.system("taskkill /f /im " + process_name)
        if exit_code == 0:
            print("Successfully kill the running process: " + process_name)
        else:
            sys.exit("Aborting...")
    else:
        # Enable less secure apps on your Google account:
        # https://myaccount.google.com/lesssecureapps
        print(process_name + " is not running." + "\n" + "Try to find .fit file(s) from GMAIL...")
        gmail = imaplib.IMAP4_SSL("imap.gmail.com")
        typ, _ = gmail.login(GMAIL_USER_ID, GMAIL_PASSWORD)
        if typ != 'OK':
            raise print('Not able to sign in!')
        typ, _ = gmail.select('Inbox')
        if typ != 'OK':
            raise print('Error searching Inbox!')
        today = datetime.date.today().strftime("%d-%b-%Y")
        typ, email_list = gmail.search(None, f'(ON {today} TO {GMAIL_USER_ID})')
        # Useful links:
        #    1. https://docs.python.org/3/library/imaplib.html#imaplib.IMAP4.search
        #    2. https://gist.github.com/martinrusev/6121028
        email_list = email_list[0].split()
        for email_id in email_list:
            download_attachments_in_email(gmail, email_id, ZWIFT_ACTIVITY_DIR)
        gmail.close()
        gmail.logout()


def upload_fit_activity_files(access_token: str):
    """
    Activity uploading related functions
    """
    os.chdir(os.path.join(ZWIFT_ACTIVITY_DIR, "FixedActivities"))
    fitfile_list = glob.glob("*.fit")
    print("\nStart uploading activity files...\n")
    #NEED FIX: bar is not callable
    with alive_bar(len(fitfile_list), title='Uploading FIT activity files', bar="blocks"): # as bar
        for fitfile in fitfile_list:
            with open(fitfile, 'rb') as fit_file:
                try:
                    base_url = "https://www.strava.com/api/v3/uploads"
                    data = {
                        'client_id': STRAVA_CLIENT_ID,
                        'data_type': 'fit'
                    }
                    header = {'Authorization': 'Bearer ' + access_token}
                    ffile = {'file': fit_file}
                    res = requests.post(
                                    base_url,
                                    data=data,
                                    headers=header,
                                    files=ffile
                                )
                except requests.exceptions.RequestException:
                    return None
                print("Uploading " + fitfile + "...")
                time.sleep(0.05)
                try:
                    upload_id = res.json().get('id_str')
                except (KeyError, TypeError, ValueError):
                    return None                    
                while True:
                    # polling the upload status per semaild
                    wait(1)
                    is_error, activity_id = check_upload_status(access_token, upload_id)
                    time.sleep(0.05)
                    # If there is an error uploading activity file or
                    # it's been successfully uploaded to Strava
                    if (is_error) or (activity_id is not None):
                        fit_file.close()
                        move_to_uploaded_or_malformed_activities_folder(fitfile)
                        if activity_id is not None:
                            print("Activity ID:", activity_id)
                            print(
                                "Check this activity here: " + 
                                "https://www.strava.com/activities/" +
                                str(activity_id)
                            )
                        # update progress bar
                        # bar() NEED FIX: is not callable
                        break
                print("")


def check_upload_status(access_token: str, upload_id: str) -> Tuple[bool, Any]:
    """
    @params:
        access_token
        upload_id
    """
    try:
        base_url = "https://www.strava.com/api/v3/uploads/" + upload_id
        header = {'Authorization': 'Bearer ' + access_token}
        r = requests.get(base_url, headers=header)
    except requests.exceptions.RequestException:
        return None    
    try:
        error_msg = r.json().get('error')
        status = r.json().get('status')
        activity_id = r.json().get('activity_id')
    except (KeyError, TypeError, ValueError):
        return None
    # Possibility 1: Your activity is still being processed
    if error_msg is None and activity_id is None:
        print(status + '.. ')
        return (False, activity_id)
    # Possibility 2: There was an error processing your activity
    # check for malformed data and duplicates
    elif error_msg:
        print(status + '.. ')
        print("Reason: " + error_msg + '\n')
        if find_whole_word('malformed')(error_msg):
            print("Please check this file in the 'UploadedOrMalformedActivities' folder!\n")
        return (True, activity_id)
    else:                                              # Possibility 3: Your activity is ready.
        print(status + '\n')
        return (False, activity_id)


def wait(poll_interval: float):
    """
    Helper
    """
    time.sleep(poll_interval)


def find_whole_word(w):
    """
    Helper
    """
    return re.compile(rf'\b({0})\b'.format(w), flags=re.IGNORECASE).search


def download_attachments_in_email(connection, email_id, download_folder):
    """
    Function to download all attachment files for a given email
    """
    try:
        # use PEEK so we don't change the UNSEEN status of the email messages
        typ, data = connection.fetch(email_id, "(BODY.PEEK[])")
        if typ != 'OK':
            raise print('Error fetching email!')
        email_body = data[0][1]
        raw_emails = email.message_from_bytes(email_body)
        for mail in raw_emails.walk():
            if mail.get_content_maintype() == 'multipart':
                continue
            if mail.get('Content-Disposition') is None:
                continue
            file_name = mail.get_filename()
            if file_name.endswith('.fit'):
                attachment_path = os.path.join(download_folder, file_name)
                if not os.path.isfile(attachment_path):
                    print('Downloading email attachment: ' + file_name + '...')
                    f = open(attachment_path, 'wb')
                    f.write(mail.get_payload(decode=True))
                    f.close()
    except:
        print('Error downloading all attachments!')
        raise
