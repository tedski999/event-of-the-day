import sys
import time
import argparse
import datetime
import calendar
import requests
import lxml.html as lh
import appdirs

WIKIPEDIA_ARTICLE_ADDR = "https://en.wikipedia.org/wiki/"
EVENTS_FILEPATH = appdirs.user_data_dir("eventoftheday", "tedski999") + "/events"
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

def download_events(args):
    all_events = []
    for month in range(1, 13):
        month_name = calendar.month_name[month]
        month_length = calendar.monthrange(VALID_LEAP_YEAR, month)[1]
        month_events = []
        for day in range(1, month_length + 1):
            time.sleep(0.01)
            address_string = WIKIPEDIA_ARTICLE_ADDR + month_name + "_" + str(day)
            print("Scrapping all historic events from " + address_string)
            #response = requests.get(address_string)
            # TODO: scrape 'events' list from downloaded web page and append each to month_events
        all_events.append(month_events)

    # TODO: write all the scrapped events to EVENTS_FILEPATH, formatted as:
    #
    # <MONTH NAME>_<DAY>:
    # <EVENT 1 YEAR>: <EVENT 1 DESCRIPTION>
    # <EVENT 2 YEAR>: <EVENT 2 DESCRIPTION>
    # etc..
    #
    # <MONTH NAME>_<DAY>:
    # etc...
    #

main()

