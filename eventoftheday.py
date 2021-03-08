#!/usr/bin/python

import os, sys, signal, datetime, calendar, json, appdirs

PROGRESS_BAR_LENGTH = 50
USER_DATA_DIR = appdirs.user_data_dir("eventoftheday", "tedski999")
API_URL = "https://en.wikipedia.org/api/rest_v1/feed/onthisday/all"
EVENT_CATEGORIES = {
    "births" : "Birthday wishes to {0}",
    "deaths" : "Rest in peace {0}",
    "events" : "{0}",
    "holidays" : "{0}"
}

USAGE_MESSAGE = """
USAGE:
    eventoftheday [-h]
    eventoftheday [-adst]
    eventoftheday download [-o]
"""

HELP_MESSAGE = f"""
A tool to download and print historic events from Wikipedia.
{USAGE_MESSAGE}
OPTIONS:
    -h --help         Print this message and exit
    -a --all          Prints every event that occurred today instead of just one
    -d --date [date]  Specify a date instead of using todays date (month/day)
    -t --type [type]  Filter events to certain types (births,deaths,events,holidays)
    -s --simple       Don't prepend the date to the output

DOWNLOAD OPTIONS:
    -o --overwrite    Overwrite any previously downloaded event files instead of skipping.

EXAMPLE USES:
    eventoftheday
        Print a random event that occurred on todays date, downloaded from Wikipedia.
        If you haven't previously downloaded this day, the days events will first have to be downloaded.
        See the download subcommand for more info.

    eventoftheday --all --simple
        Prints every downloaded event that occurred today, without the date prepended.
        If none are found, they will be fetched from Wikipedia.

    eventoftheday --type births,deaths
        Only print events that are either the birth or death of an historical figure.

    eventoftheday --date 01/02 --all
        All the downloaded events that occurred on the 2nd of January will be printed.

    eventoftheday download --overwrite
        Download the events of every day in the year from Wikipedia.
        Overwrite any previously downloaded event files.
        Note that this command can take some time.

Ted Johnson 2021 (tedjohnsonjs@gmail.com)
eventoftheday v2.0 - MIT License
"""

def main():
    signal.signal(signal.SIGINT, int_signal_handler)

    # Default arguments
    func = print_events
    args = {
        "date" : datetime.datetime.now(),
        "categories" : EVENT_CATEGORIES,
        "all" : False,
        "simple" : False
    }

    # Apply command-line arguments
    i = 1
    if len(sys.argv) > 1 and sys.argv[1] == "download":
        func = download_events
        args = { "overwrite" : False }
        i += 1
    while i < len(sys.argv):

        try:
            if func is print_events and sys.argv[i] in ("-d", "--date"):
                i += 1
                if i >= len(sys.argv):
                    raise Exception("Missing argument after " + sys.argv[i - 1])
                args["date"] = parse_date(sys.argv[i])
            elif func is print_events and sys.argv[i] in ("-t", "--type"):
                i += 1
                if i >= len(sys.argv):
                    raise Exception("Missing argument after " + sys.argv[i - 1])
                args["categories"] = parse_categories(sys.argv[i])
            elif func is print_events and sys.argv[i] in ("-a", "--all"):
                args["all"] = True
            elif func is print_events and sys.argv[i] in ("-s", "--simple"):
                args["simple"] = True
            elif func is download_events and sys.argv[i] in ("-o", "--overwrite"):
                args["overwrite"] = True
            elif sys.argv[i] in ("-?", "-h", "--help"):
                print(HELP_MESSAGE, end="")
                quit(0)
            else:
                raise Exception("Unknown argument: " + sys.argv[i])

        except Exception as err:
            sys.stderr.write(str(err) + "\n" + USAGE_MESSAGE)
            quit(1)

        i += 1

    # Execute the appropriate function with the provided arguments
    func(args)

# Print the downloaded historic events for a date
def print_events(args):
    events = get_day_events(args["date"].month, args["date"].day, args["categories"])
    if not args["all"]:
        import random
        events = [random.choice(events)]
    for event in events:
        if not args["simple"]:
            print("{0} {1}".format(calendar.month_name[args["date"].month], get_ordinal(args["date"].day)), end="")
            if "year" in event:
                print(", {0}".format(event["year"]), end="")
            print(" - ", end="")
        print(event["text"])

# Returns a list of historic events for month and day
def get_day_events(month, day, categories):
    events = []
    directory = os.path.join(USER_DATA_DIR, str(month), str(day))
    for filename in categories:
        filepath = os.path.join(directory, filename)
        if not os.path.isfile(filepath):
            sys.stderr.write("Events file for {0}/{1} not found, downloading now...\n".format(month, day))
            fetch_day_events(month, day)
        with open(filepath, "r") as file:
            events.extend(json.load(file))
    return events

# Fetches and stores events from the Wikipedia API
def download_events(args):
    import time

    print("Downloading historic events from the Wikipedia API...")

    # Loop through every day of the year
    month_lengths = [ 31, 29, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31 ]
    for month in range(0, len(month_lengths)):
        month_length = month_lengths[month]
        month_name = calendar.month_name[month + 1]
        for day in range(0, month_lengths[month]):

            # Draw progress bar
            progress = day / (month_length - 1)
            progress_steps = int(PROGRESS_BAR_LENGTH * progress)
            progrss_bar = "█" * progress_steps + '-' * (PROGRESS_BAR_LENGTH - progress_steps)
            print("\r{0: <12} |{1}| {2:.1f}%".format(month_name + " " + str(day + 1), progrss_bar, progress * 100), end = "\r")

            # Download day of events
            if args["overwrite"] or not os.path.isdir(os.path.join(USER_DATA_DIR, str(month + 1), str(day + 1))):
                fetch_day_events(month + 1, day + 1)
                time.sleep(0.025)

        print()

# Fetch events from the Wikipedia API for a date
def fetch_day_events(month, day):
    import requests

    # Download events
    url = "{0}/{1:02d}/{2:02d}".format(API_URL, month, day)
    try:
        response = requests.get(url)
        if response.status_code != 200:
            raise Exception("Received error code " + str(response.status_code))
        received_events = response.json()
    except Exception as err:
        sys.stderr.write("Could not get {0}:\n{1}\n".format(url, err))
        quit(1)

    try:
        # Make sure the directory exists before writing to it
        directory = os.path.join(USER_DATA_DIR, str(month), str(day))
        if not os.path.isdir(directory):
            os.makedirs(directory, exist_ok = True)

        # Write a new file for each event category
        for category in EVENT_CATEGORIES:
            with open(os.path.join(directory, category), "w") as file:

                # Convert received events to our own format
                for event in received_events[category]:
                    del event["pages"]
                    if "year" in event:
                        event["year"] = str(event["year"]) if event["year"] >= 0 else str(-event["year"]) + " BC"
                    event["text"] = EVENT_CATEGORIES[category].format(event["text"].replace("\n", " "))

                # Write JSON to file
                json.dump(received_events[category], file)

    except Exception as err:
        sys.stderr.write("Unable to write events file:\n{0}\n".format(err))
        quit(1)

# Returns the appropriate suffix for a number
def get_ordinal(number):
    suffix = "th"
    if not 11 <= number % 100 <= 13:
        suffix = ["th", "st", "nd", "rd", "th"][min(number % 10, 4)]
    return str(number) + suffix

# Parse a datetime object from a provided string
def parse_date(date_string):
    return datetime.datetime.strptime(date_string, "%m/%d")

# Parse event filters from a provided string
def parse_categories(categories_string):
    categories = categories_string.lower().split(",")
    if not all(category in EVENT_CATEGORIES for category in categories):
        raise Exception("Invalid event type filter " + categories_string)
    return categories

# Exit gracefully when receiving SIGINT
def int_signal_handler(sig, frame):
    quit(1)

main()

