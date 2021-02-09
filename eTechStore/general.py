import os
import pickle
import time
import pprint
import uuid
import sys

from scrapy.utils.project import get_project_settings

# OUTPUT_DIR = r'E:/scrapy_outputs/'
THIS_DIR = os.path.dirname(__file__)
OUTPUT_DIR = os.path.abspath(os.path.join(THIS_DIR, '../outputs'))
FILE_ALL_ITEMS = os.path.abspath(os.path.join(THIS_DIR, 'all_items.txt'))
FILE_NEW_ITEMS = os.path.abspath(os.path.join(THIS_DIR, 'new_items.txt'))
DB_URL = f'sqlite:///{os.path.join(OUTPUT_DIR, "db", "UrlsManager.sqlite")}'
PROXY_FILE = os.path.join(THIS_DIR, "proxy.txt")

def read_file_lines(file_path=""):
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf8") as file_:
            return [line_.strip().replace("\n", "").replace("\r", "").replace("\l", "") for line_ in file_.readlines() if line_.strip()]
    return []


def write_file(file_path="", content="", mode='a'):
    with open(file_path, mode, encoding="utf8") as file_:
        file_.write(content)

def append_lines_file(file_path="", lst_line =[]):
    write_file(file_path, "\n".join(read_file_lines(file_path) + lst_line), "w+")

def write_new_links(lst_links=[]):
    if lst_links:
        lst_all_links = read_file_lines(FILE_ALL_ITEMS)
        lst_new = list(set(lst_links) - set(lst_all_links))

        if lst_new:
            lst_new.sort()
            append_lines_file(FILE_NEW_ITEMS, lst_new)
            append_lines_file(FILE_ALL_ITEMS, lst_new)

def save_pickle(file_path="", data=None):
    with open(file_path, "ab") as file_:
        pickle.dump(data, file_)

def load_pickle(file_path=""):
    with open(file_path, 'rb') as file_:
        return pickle.load(file_)

def get_log_dir(spider_name=""):
    return os.path.join(OUTPUT_DIR, 'crawls', spider_name)

def get_data_dir(name=""):
    if not name:
        bot_name = get_project_settings().get("BOT_NAME")
        name = f'{bot_name}_data_{time.strftime("%Y%m%d-%H%M%S")}'
    return os.path.join(OUTPUT_DIR, 'data', name)

def get_uuid():
    return str(uuid.uuid4())

# Print iterations progress
def print_progress_bar (iteration, total, prefix = '', suffix = '', decimals = 1, length = 100, fill = '█', printEnd = "\n"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    msg = f'\r{prefix} |{bar}| {percent}% {suffix}'
    # print(msg, end = printEnd)
    sys.stdout.write(msg)
    sys.stdout.flush()

    # print(f'\r{prefix} |{bar}| {percent}% {suffix}')
    # Print New Line on Complete
    if iteration == total:
        print()