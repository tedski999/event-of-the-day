#!/usr/bin/python

import os
import sys
import signal
import argparse
import datetime
import calendar
import appdirs

WIKIPEDIA_ARTICLE_ADDR = "https://en.wikipedia.org/wiki/"
USER_DATA_DIR = appdirs.user_data_dir("eventoftheday", "tedski999")
VALID_LEAP_YEAR = 2012

def main():
    signal.signal(signal.SIGINT, int_signal_handler)
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter,
        description="Downloads and prints major historic events from Wikipedia",
        epilog="Note: This script is not future-proof, as Wikipedia's day articles may change in format!\n\nTed Johnson, 2020")
    subparser = parser.add_subparsers(metavar="commands", required=True)
    subparser_random = subparser.add_parser("random", usage="%(prog)s [-h] [-d date]", help="prints a random historic event that occurred on todays date")
    subparser_random.add_argument(
        "-d", "--date", metavar="date",
        type=date, default=datetime.datetime.now().strftime("%m/%d"),
        help="override the date of the historic events (format: MONTH/DAY)")
    subparser_random.set_defaults(func=print_random_event)
    subparser_events = subparser.add_parser("events", usage="%(prog)s [-h] [-d date]", help="prints a list of all the historic events that occurred on todays date", )
    subparser_events.add_argument(
        "-d", "--date", metavar="date",
        type=date, default=datetime.datetime.now().strftime("%m/%d"),
        help="override the date of the historic events (format: MONTH/DAY)")
    subparser_events.set_defaults(func=print_events)
    subparser.add_parser("download", usage="%(prog)s [-h]", help="downloads all the historic events from Wikipedia (https://en.wikipedia.org/wiki/Category:Days)").set_defaults(func=download_events)
    args = parser.parse_args()
    args.func(args)

# Print a randomly selected historic event for the date
def print_random_event(args):
    import random
    day_suffix = ["th", "st", "nd", "rd", "th"][min(args.date.day % 10, 4)]
    if 11 <= (args.date.day % 100) <= 13:
        day_suffix = "th"
    month_name = calendar.month_name[args.date.month]
    print("{0} {1}, {2}".format(month_name, str(args.date.day) + day_suffix, random.choice(get_day_events(month_name, str(args.date.day)))))

# Print all the downloaded historic events for the date
def print_events(args):
    print(*get_day_events(calendar.month_name[args.date.month], str(args.date.day)), sep="\n")

# Scrapes all of the Wikipedia day articles for historic events
def download_events(args):
    print("Downloading all historic events listed on the Wikipedia day articles...")

    import re
    import time
    import requests
    from bs4 import BeautifulSoup

    # Loop through every month
    for month in range(1, 13):

        # Loop through every day in the month
        month_name = calendar.month_name[month]
        month_length = calendar.monthrange(VALID_LEAP_YEAR, month)[1]
        for day in range(1, month_length + 1):
            day_events = []

            # Download and begin parsing the Wikipedia page
            time.sleep(0.01)
            address_string = WIKIPEDIA_ARTICLE_ADDR + month_name + "_" + str(day)
            print("Scraping {0}...".format(address_string))
            try:
                page = requests.get(address_string, timeout=5)
                soup = BeautifulSoup(page.content, "html.parser")
            except requests.exceptions.RequestException as err:
                sys.stderr.write("An error occurred while trying to download {0}:\n{1}".format(address_string, err))
                quit(1)

            # Locate and loop through every event on the page
            year_events_tag = soup.find("span", class_="mw-headline", id="Events").parent
            next_tag = year_events_tag.next_sibling.next_sibling
            while next_tag.name != "h2":
                if next_tag.name == "ul":
                    for next_list_item in next_tag.find_all("li"):

                        # Remove citation tags
                        for sup_tag in next_list_item("sup"):
                            sup_tag.decompose()

                        # Parse valid text and save to day_events
                        text = next_list_item.get_text()
                        event_data = text.split(" – ")
                        if len(event_data) == 2 and re.match(r"^[0-9]+\s+((BC|AD)\s+)?–.+$", text):
                            day_events.append(event_data[0].strip() + " – " + event_data[1].strip())

                # Go to the next tag
                next_tag = next_tag.next_sibling.next_sibling

            # Save all the parsed day events to disk
            day_file_path = "{0}/{1}_{2}".format(USER_DATA_DIR, month_name, day)
            if not os.path.isdir(USER_DATA_DIR):
                os.mkdir(USER_DATA_DIR)
            with open(day_file_path, "w") as day_file:
                day_file.write("\n".join(day_events))

    print("Done!")

# Parse a datetime object from a provided string
def date(date_string):
    date = datetime.datetime.strptime(date_string, "%m/%d")
    return date

# Read and return a list of historic events for month and day
def get_day_events(month, day):

    # Attempt to open the events data file
    day_file_path = "{0}/{1}_{2}".format(USER_DATA_DIR, month, day)
    try:
        day_file = open(day_file_path, "r")
    except OSError:
        sys.stderr.write("Could not open day events data: {0}\nHave you downloaded the events from Wikipedia with 'eventoftheday download'?\n".format(day_file_path))
        quit(1)

    # Load events from disk
    with day_file:
        day_events = [line.rstrip() for line in day_file]

    return day_events

# Exit gracefully when receiving SIGINT
def int_signal_handler(sig, frame):
    quit(1)

main()

