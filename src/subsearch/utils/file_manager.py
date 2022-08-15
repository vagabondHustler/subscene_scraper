import os
import shutil
import struct
import zipfile

import cloudscraper

from . import log, string_parser

SCRAPER = cloudscraper.create_scraper(browser={"browser": "chrome", "platform": "android", "desktop": False})


# download zip files from url
def download_zip(item: str) -> None:
    """
    download zip file from url

    Args:
        item (str): url to download
    """
    file_path, url, current_num, total_num = item
    log.output(f"Downloading: {current_num}/{total_num}")
    r = SCRAPER.get(url, stream=True)
    with open(file_path, "wb") as fd:
        for chunk in r.iter_content(chunk_size=1024):
            fd.write(chunk)


# extract all zip file in said directory
def extract_zips(cwd: str, extension: str) -> None:
    """
    extract all zip file in said directory that start with __subsearch__

    Args:
        cwd (str): directory to extract zip files from
        extension (str): extension to extract
    """
    subs_folder = os.path.join(cwd, "subs")
    if not os.path.exists(subs_folder):
        os.mkdir(subs_folder)
    for file in os.listdir(cwd):
        if file.startswith("__subsearch__") and file.endswith(extension):
            log.output(f"Extracting: {file} -> ..\\subs\\{file}")
            file_name = os.path.join(cwd, file)
            # file_name = os.path.abspath(file)
            zip_ref = zipfile.ZipFile(file_name)
            zip_ref.extractall(subs_folder)
            zip_ref.close()


# rename a .srts to the same as video release name
def rename_best_match(release_name: str, cwd: str, extension: str) -> None:
    """
    rename the best matching srt file compared to the video file for e.g MPC-HC to auto import

    Args:
        release_name (str): name of the video name
        cwd (str): current working directory
        extension (str): suffix of the subtitle file
    """
    higest_value = (0, "")
    subs_folder = os.path.join(cwd, "subs")
    for file in os.listdir(subs_folder):
        if file.endswith(extension):
            value = string_parser.pct_value(file, release_name)
            if value >= higest_value[0]:
                higest_value = value, file

    file_to_rename = higest_value[1]
    old_name_src = os.path.join(subs_folder, file_to_rename)
    new_name_dst = os.path.join(subs_folder, release_name)
    log.output(f"Renaming: {file} -> {release_name}")
    os.rename(old_name_src, new_name_dst)
    move_src = new_name_dst
    move_dst = os.path.join(cwd, release_name)
    log.output(f"Moving: {release_name} -> {cwd}")
    shutil.move(move_src, move_dst)


# remove .zips
def clean_up(cwd: str, extension: str) -> None:
    """
    Remove all the temporary files in the current working directory

    Args:
        cwd (str): current working directory
        extension (str): suffix of the file to remove
    """
    for file in os.listdir(cwd):
        if file.startswith("__subsearch__") and file.endswith(extension):
            log.output(f"Removing: {file}")
            file_path = os.path.join(cwd, file)
            os.remove(file_path)


# get file hash
def get_hash(file_name: str) -> str | None:
    """
    Tries to get the hash of the file

    Args:
        file_name (str): path/file_name to get the hash of

    Returns:
        str | None: the hash of the file or None if the size is 0
    """
    try:
        longlongformat = "<q"  # little-endian long long
        bytesize = struct.calcsize(longlongformat)
        with open(file_name, "rb") as f:
            filesize = os.path.getsize(file_name)
            hash = filesize
            if filesize < 65536 * 2:
                log.output(f"SizeError: filesize is {filesize} bytes", False)
                return None
            n1 = 65536 // bytesize
            for _x in range(n1):
                buffer = f.read(bytesize)
                (l_value,) = struct.unpack(longlongformat, buffer)
                hash += l_value
                hash = hash & 0xFFFFFFFFFFFFFFFF  # to remain as 64bit number
            f.seek(max(0, filesize - 65536), 0)
            n2 = 65536 // bytesize
            for _x in range(n2):
                buffer = f.read(bytesize)
                (l_value,) = struct.unpack(longlongformat, buffer)
                hash += l_value
                hash = hash & 0xFFFFFFFFFFFFFFFF

        returnedhash = "%016x" % hash
        return returnedhash

    except IOError as err:
        return log.output(err)
