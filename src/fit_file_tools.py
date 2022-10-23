"""
Automation with selenium
"""
import os
import sys
import time
import glob
from datetime import datetime
from typing import Any
import pyautogui
import pyperclip
from alive_progress import alive_bar
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from file_manipulation import move_to_original_activities_folder, rename_fit_file, move_to_fixed_activities_folder
from environment import ZWIFT_ACTIVITY_DIR


def fix_fit_activity_files():
    """
    FIT File Tools automation
    """
    owd = os.getcwd()
    os.chdir(ZWIFT_ACTIVITY_DIR)
    fitfile_list = glob.glob("*.fit")
    if 'inProgressActivity.fit' in fitfile_list:
        fitfile_list.remove('inProgressActivity.fit')
    if not fitfile_list:
        sys.exit("\nNo .fit file(s) to be fixed and uploaded to Strava.\nAborting...")
    else:
        print('\nWorkout data found: ', end="")
        for fit in fitfile_list:
            print('\n\t' + fit, end="")
        print('\n')
        with alive_bar(
            1,
            title='Opening the webpage of FIT File Tools',
            bar="blocks",
            spinner="classic") as bar:
            dir_name = os.path.dirname(__file__)
            web_driver_bar = os.path.abspath(
                os.path.join(
                    dir_name,
                    '..',
                    'webdriver',
                    'geckodriver.exe'
                    )
                )
            log_file_path = os.path.abspath(
                os.path.join(
                    dir_name,
                    '..',
                    'logfile',
                    'geckodriver.log'
                    )
                )
            driver = webdriver.Firefox(
                executable_path=web_driver_bar,
                service_log_path=log_file_path
                )
            # Step 1: open the webpage of FIT File Tools
            driver.get("https://www.fitfiletools.com/#/top")            
            # update progress bar
            # bar() NEED FIX: is not callable

        with alive_bar(len(fitfile_list), title='Fixing FIT activity files', bar="blocks") as bar:
            for fitfile in fitfile_list:           
                path_to_fitfile = os.path.join(ZWIFT_ACTIVITY_DIR, fitfile)
                # check if the size of the fit file is smaller than 10KB
                if os.path.getsize(path_to_fitfile) < 10000:
                    move_to_original_activities_folder(fitfile)
                    # update progress bar
                    time.sleep(1)
                else:
                    try:
                        bar.text("Fixing " + fitfile + "...")
                        # Step 2: click the "Launch" button of "Time Adjuster"
                        element = WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located((By.XPATH, "//a[@href='#/adjuster']"))
                        )
                        element.click()
                        # Step 3: click the "... or select files" button
                        element = WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located(
                                (By.XPATH, "//button[@ng-file-select='']")
                            )
                        )
                        element.click()
                        time.sleep(1)
                        # Step 4: select the corresponding fit file to be fixed
                        pyperclip.copy(path_to_fitfile)   # copy to clipboard
                        pyautogui.hotkey('ctrl', "v")   # ctrl-v to paste from clipboard
                        finish_file_selection(element)
                        time.sleep(1)
                        # Step 5: select the start date of the activity
                        fit_filename = fitfile.split('-')
                        # convert a month number to a month name
                        fit_filename[1] = datetime.strptime(fit_filename[1], "%m").strftime("%B")
                        # convert time from 24-hour clock format to 12-hour clock format
                        hours = int(fit_filename[3])
                        if hours > 12:
                            afternoon = True
                            hours -= 12
                        else:
                            afternoon = False
                            if hours == 0:   # special case
                                hours = 12
                        element = WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located((By.XPATH, "//input[@ng-model='dt']"))
                        )
                        element.clear()
                        dd_mm_yyyy = fit_filename[2] + '-' + fit_filename[1] + '-' + fit_filename[0]
                        element.send_keys(dd_mm_yyyy)
                        time.sleep(1)
                        # Step 6: select the start time (hours & minutes) of the activity
                        # fill in minutes
                        element = WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located(
                                (By.XPATH, "//input[@ng-model='minutes']")
                            )
                        )
                        element.clear()
                        element.send_keys(fit_filename[4])
                        time.sleep(1)
                        # choose A.M. or P.M.
                        if afternoon:
                            element = WebDriverWait(driver, 5).until(
                                EC.presence_of_element_located(
                                    (By.XPATH, "//button[@ng-click='toggleMeridian()']")
                                )
                            )
                            element.click()
                            time.sleep(1)                            
                        # fill in hours
                        element = WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located((By.XPATH, "//input[@ng-model='hours']"))
                        )
                        element.clear()
                        element.send_keys(str(hours))
                        time.sleep(1)
                        # Step 7: start fixing the activity file
                        element = WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located((By.XPATH, "//a[@ng-click='adjust()']"))
                        )
                        element.click()
                        # Step 8: download your file
                        element = WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located(
                                (By.LINK_TEXT, 'Click here to download your file!')
                            )
                        )
                        element.click()
                        time.sleep(3)
                        # pyautogui.press('return')
                        # time.sleep(3)
                        # update progress bar
                        # bar() NEED FIX: is not callable
                        # Step 9: click the "Close" button of "Time Adjuster"
                        element = WebDriverWait(driver, 5).until(
                            EC.presence_of_element_located((By.LINK_TEXT, '« Close'))
                        )
                        element.click()
                        # Step 10:rename file in Downloads folder and move to FixedActivities folder
                        newfilename = fit_filename[1] + fit_filename[2] + '.fit'   # mmdd.fit
                        rename_fit_file(newfilename)
                        move_to_fixed_activities_folder(newfilename)
                        # Step 11: move the original fit file in ZWIFT_ACTIVITY_DIR to
                        # OriginalActivities folder
                        move_to_original_activities_folder(fitfile)
                    except TimeoutException:
                        print("ERROR - Timeout!")
                        driver.quit()
                    except NoSuchElementException:
                        print("ERROR - Cannot find the element!")
                        driver.quit()
        # Step 12: close the web browser window and change back to the original working directory
        driver.quit()
        os.chdir(owd)
        print()


def finish_file_selection(element: Any):
    """
    Finish
    """
    try:
        # simulate a single, left-button mouse click at the mouse’s current position
        pyautogui.click()
    except element:
        # in case the mouse's click doesn't work...
        element.send_keys(Keys.RETURN)
 