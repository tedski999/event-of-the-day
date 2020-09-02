import os
import sys
import time
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
    # TODO: -d / --date argument to specify a date instead of the default of today
    # TODO: remove ... from usage and subcommand metavar from subcommands list
    parser = argparse.ArgumentParser()
    subparser = parser.add_subparsers(metavar="subcommand", required=True, dest="subcommand")
    subparser.add_parser("random", help="prints a random historic event that occurred on todays date").set_defaults(func=print_random_event)
    subparser.add_parser("events", help="prints a list of all the historic events that occurred on todays date").set_defaults(func=print_events)
    subparser.add_parser("download", help="downloads all the historic events from Wikipedia (https://en.wikipedia.org/wiki/Category:Days)").set_defaults(func=download_events)
    args = parser.parse_args()
    args.func(args)

def print_random_event(args):
    try:
        events_file = open(EVENTS_FILEPATH, "r")
    except OSError:
        sys.stderr.write("Could not open events data: " + EVENTS_FILEPATH + "\nHave you downloaded the events from Wikipedia with 'eventoftheday download'?\n")
        quit(1)

    with events_file:
        date_string = datetime.datetime.now().strftime("%MMMM_%d")
        # TODO: find relevant events from events_file

    # TODO: print a random event

def print_events(args):
    print("TODO: list events")

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

main()

