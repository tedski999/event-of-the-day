# Event of the Day

Prints random historic events that occurred on today's date from Wikpedia articles.

## Getting Started

This script was intended to be used as a terminal greeting or in a notification message. It was developed primarily for Linux, but I see no difficulty in modifying and using it with other platforms.

As such, the instruction below will assume Linux is the target platform.

### Prerequisites

The script is written in Python 3, so you're going to need Python. It's presumed to be located at `/usr/bin/python`.

The following Python packages are used:

 - [appdirs](https://pypi.org/project/appdirs) for platform-agnostic file directories
 - [requests](https://requests.readthedocs.io) for HTTP page downloading

All of them can be installed easily using `pip` or following instructions found on their websites.

### Installation

The easiest method is to place the [eventoftheday.py](eventoftheday.py) script somewhere on your systems path. For example, placing the script in `/usr/local/bin` lets you execute the script anywhere with `eventoftheday.py`. Better yet, renaming the script to `eventoftheday` means you can simply call `eventoftheday`.

Alternatively, you can specify the full path to the script when calling instead of placing it on your system's path. Below, it's assumed the script is on the system's path.

### Usage

If you don't want to constantly be downloading Wikipedia events for the next year, it's probably a good idea to get them all downloaded now. We can automatically download the entire year of events with this command:

```sh
$ eventoftheday download
```

This command may take a while, so it's best left to do its thing. The downloaded events are stored in your user data directory, such as `~/.local/share/eventoftheday/`.

If you ever want to re-download the event files, add the `--overwrite` flag to overwrite your previous files.

Now with all the major historic events downloaded, we can use the following commands to print them:
```sh
$ eventoftheday
```

By default, this will print a single historic event *that occurred on today's date* picked at random. To change which date to use, add the `--date` argument:
```sh
$ eventoftheday --date 05/01
```
This argument takes the format ***month/day***, so the above will print out all the major historic events that occurred on the 1st of May.

It's also possible to print all the events that occurred on the selected date:
```sh
$ eventoftheday --all
```

If your only interested in seeing the births and deaths of historical figures, you can filter which events get picked:
```sh
$ eventoftheday --filter births,deaths
```
There are 4 filters available: `events,births,deaths,holidays`

If your only interested in seeing the births and deaths of historical figures, you can filter which events get picked:
```sh
$ eventoftheday --filter births,deaths
```
There are 4 filters available: `events,births,deaths,holidays`

To prevent the date from being prepended to the output, set the `--simple` flag:
```sh
$ eventoftheday --simple
```


Finally, if you're ever stuck, help is available with the usual suspects:
```sh
$ eventoftheday -h
```

## Possible Future Improvements

- The Wikimedia REST API is rather slow. Article scrapping was faster. It's worthwhile to look into alternatives.
	- It may be beneficial to fetch compressed data and uncompress locally instead.
- It might be helpful to be able to specify a year range or several dates at once.
- The events come along with links to appropriate Wikipedia articles. However, we're currently just discarding them. It could be a nice option to include them.

## References

- Project idea found on [lainchan.org](https://lainchan.org) programming board.
- This project makes use of the [Wikimedia REST API](https://en.wikipedia.org/api/rest_v1/) for downloading events.
- The Wikipedia articles for each day can be found [here](https://en.wikipedia.org/wiki/Category:Days)

Ted Johnson 2021 (tedjohnsonjs@gmail.com)\
eventoftheday v2.0 - [MIT License](LICENSE.md)
