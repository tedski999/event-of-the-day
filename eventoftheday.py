#!/usr/bin/python

import os
import sys
import time
import random
import json
import re
import argparse
import datetime
import calendar
import requests
import appdirs
from bs4 import BeautifulSoup

WIKIPEDIA_ARTICLE_ADDR = "https://en.wikipedia.org/wiki/"
USER_DATA_DIR = appdirs.user_data_dir("eventoftheday", "tedski999")
EVENTS_FILEPATH = USER_DATA_DIR + "/events"
VALID_LEAP_YEAR = 2012

def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter,
        description="Downloads and prints major historic events from Wikipedia",
        epilog="Note: This script is not future-proof, as Wikipedias day articles may change in format!\n\nTed Johnson, 2020")
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
    day_suffix = ["th", "st", "nd", "rd", "th"][min(args.date.day % 10, 4)]
    if 11 <= (args.date.day % 100) <= 13:
        day_suffix = "th"
    month_name = calendar.month_name[args.date.month]
    print(month_name, str(args.date.day) + day_suffix + ",", random.choice(get_day_events(month_name, str(args.date.day))))

# Print all the downloaded historic events for the date
def print_events(args):
    print(*get_day_events(calendar.month_name[args.date.month], str(args.date.day)), sep="\n")

# Scrapes all of the Wikipedia day articles for historic events
def download_events(args):
    print("Downloading all historic events listed on the Wikipedia day articles...")

    # Loop through every month
    all_events = {}
    for month in range(1, 13):

        # Loop through every day in the month
        month_name = calendar.month_name[month]
        month_length = calendar.monthrange(VALID_LEAP_YEAR, month)[1]
        month_events = {}
        for day in range(1, month_length + 1):
            day_events = []

            # Download and begin parsing the Wikipedia page
            # TODO: error handling
            time.sleep(0.01)
            address_string = WIKIPEDIA_ARTICLE_ADDR + month_name + "_" + str(day)
            print("Scraping " + address_string + "...")
            page = requests.get(address_string)
            soup = BeautifulSoup(page.content, "html.parser")

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

            # Save all the parsed day events to a key on the month_events object
            month_events[str(day)] = day_events

        # Save the month object to a key on the all_events object
        all_events[month_name] = month_events

    # Write events to a JSON file
    print("Writing parsed events data to disk...")
    data = json.dumps(all_events, indent=4)
    if not os.path.isdir(USER_DATA_DIR):
        os.mkdir(USER_DATA_DIR)
    with open(EVENTS_FILEPATH, "w") as events_file:
        events_file.write(data)

# Parse a datetime object from a provided string
def date(date_string):
    date = datetime.datetime.strptime(date_string, "%m/%d")
    return date

# Read in JSON data from events file and return array of historic events for month and day
def get_day_events(month, day):

    # Attempt to open the events data file
    try:
        events_file = open(EVENTS_FILEPATH, "r")
    except OSError:
        sys.stderr.write("Could not open events data: " + EVENTS_FILEPATH + "\nHave you downloaded the events from Wikipedia with 'eventoftheday download'?\n")
        quit(1)

    # Load JSON object from file
    with events_file:
        events_data = json.load(events_file)
        day_events = events_data[month]
        day_events = day_events[day]
    return day_events

main()

