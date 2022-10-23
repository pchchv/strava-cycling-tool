"""
Strava Upload Tool
"""

import os
import sys
import imaplib
import subprocess
import datetime
import email
from environment import GMAIL_USER_ID, GMAIL_PASSWORD, ZWIFT_ACTIVITY_DIR


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
