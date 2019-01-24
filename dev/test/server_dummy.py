from __future__ import print_function
import argparse
import time
import datetime
import os
from dateutil import parser as dateparser
import sys

mac_lib_path = os.path.expanduser("~/work/pa/PersonalAssistant")
win_lib_path = 'C:\\Users\\Petr\\Desktop\\HomeAutomation\\PersonalAssistant'


def is_mac():
    val = os.path.join('_', '_')
    return val == "_/_"


if is_mac():
    if mac_lib_path not in sys.path:
        sys.path.append(mac_lib_path)
else:
    if win_lib_path not in sys.path:
        sys.path.append(win_lib_path)

from pyutils import write, read, trim


def get_fp(name):
    return os.path.join('data', name)


error_file_name = "error_log.txt"
error_file_path = get_fp(error_file_name)


def get_latest_online_time():
    files = os.listdir("data")
    last_log_file_name = list(sorted([f for f in files if f.startswith("20") and len(f) == 17]))[-1]
    last_log_file_path = get_fp(last_log_file_name)

    last_message = read(last_log_file_path).strip().split('\n')[-1]

    return dateparser.parse(trim(last_message, s="Server online on ").split('.')[0].strip())


def log_error(message):
    write(message, error_file_path, mode='a')


def main():
    while True:
        ts = datetime.datetime.now()

        last_online = get_latest_online_time()

        offline_period = ts - last_online

        if offline_period > datetime.timedelta(minutes=10):
            print("Last online: ", last_online.strftime("%Y/%m/%d at %H:%M:%S"))
            print("Offline period: {} hours, {} minutes".format(offline_period.seconds / 3600,
                                                                (offline_period.seconds / 60) % 60))
            write("WARNING: Server relaunch on {}. Offline for ".format(ts.strftime("%Y/%m/%d at %H:%M:%S"), offline_period),
                  error_file_path)
        #
        # except:
        #     write("WARNING: Failed to get latest online time on {}".format(ts.strftime("%Y/%m/%d at %H:%M:%S")), error_file_path)
        #     print("Failed get latest online time ")

        file_name = "{ts}.txt".format(ts=ts.strftime("%Y-%m-%d_%H"))
        file_path = os.path.join('data', file_name)

        from pyutils import connected_to_internet
        connected = connected_to_internet()

        message = "Server online on {}. Connected to internet: {} \n".format(ts.strftime("%Y/%m/%d at %H:%M:%S"), connected)
        write(message, file_path)
        print(message)
        if not connected:
            log_error("WARNING: No internet connection on {}".format(ts.strftime("%Y/%m/%d at %H:%M:%S")))


        time.sleep(60)


if __name__ == "__main__":
    main()
    try:
        main()
    except Exception as e:
        ts = datetime.datetime.now()
        log_error("WARNING: Launch failed on {} \n exception: {}".format(ts.strftime("%Y/%m/%d at %H:%M:%S"), e))
        raise e

