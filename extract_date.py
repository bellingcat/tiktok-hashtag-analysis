#!/usr/bin/env python3

import sys
import json
import datetime
import collections
import matplotlib.pyplot as plt
import matplotlib.dates as mdates


if len(sys.argv) < 3:
    print(f'ERROR: Please make sure the command line has the following format: python3 extract_date.py hashtag_data.json hashtag')
    sys.exit()


def list_to_frequency(li):
    if li and (type(li) == list):
        return collections.Counter(li)
    else:
        print(f"ERROR: either {li} is empty or not a list.")


def eligibility_check(obj):
    if not obj:
        print(f'ERROR: {obj} is empty!')
        return False
    elif type(obj) != int:
        print(f'ERROR: {obj} is not an integer as is expected!')
        return False
    else:
        return True

with open(sys.argv[1]) as file:
    object = json.load(file)
    l = len(object)
    date_list = []
    for i in range(0, l):
        obj = object[i]["createTime"]
        if eligibility_check(obj):
            dt_obj = datetime.datetime.fromtimestamp(obj)
            date_list.append(dt_obj.date())
        else:
            print(f'ERROR: Some error occured. Check {obj}.')
    ordered = dict(list_to_frequency(date_list))
    dates = list(ordered.keys())
    total_dates = len(dates)
    frequency = list(ordered.values())
    plt.scatter(dates, frequency)
    plt.gcf().autofmt_xdate()
    date_format = mdates.DateFormatter('%d-%m-%Y')
    plt.gca().xaxis.set_major_formatter(date_format)
    plt.tight_layout()
    plt.title(f'Hashtag Lifecyle - #{sys.argv[2]}')
    plt.xlabel(f'Dates ({total_dates} dates out of {l} posts)')
    plt.ylabel('Posts')
    plt.show()
