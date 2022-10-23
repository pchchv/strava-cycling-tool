"""
File manipulations
"""

import os
import shutil
from pathlib import Path
from enviroment import ZWIFT_ACTIVITY_DIR


def move_to_fixed_activities_folder(filename: str):
    """
    @params:
        filename
    """
    source_dir = os.path.join(Path.home(), "Downloads")
    dest_dir = os.path.join(ZWIFT_ACTIVITY_DIR, "FixedActivities")
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
    source = os.path.join(source_dir, filename)
    dest = os.path.join(dest_dir, filename)
    shutil.move(source, dest)

def move_to_original_activities_folder(filename: str):
    """
    @params:
        filename
    """
    dest_dir = os.path.join(ZWIFT_ACTIVITY_DIR, "OriginalActivities")
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
    source = os.path.join(ZWIFT_ACTIVITY_DIR, filename)
    dest = os.path.join(dest_dir, filename)
    shutil.move(source, dest)

def rename_fit_file(newfilename: str, fitfilename: str="fitfiletools.fit"):
    """
    @params:
        newfilename
    """
    old_filename = os.path.join(Path.home(), "Downloads", fitfilename)
    new_filename = os.path.join(Path.home(), "Downloads", newfilename)
    os.rename(old_filename, new_filename)
