# Event of the Day

Prints random historic events that occurred on today's date from articles automatically scrapped from Wikipedia.

## Getting Started

This script was intended to be used as a terminal greeting or in a notification message. It was developed primarily for Linux, but I see no difficulty in modifying and using it with other platforms.

As such, the instruction below will assume Linux is the target platform.

### Prerequisites

The script is written in Python 3, so a valid Python interpreter is needed on the system. The interpreter is presumed to be located at `/usr/bin/python`.

The following Python packages are used:

 - [appdirs](https://pypi.org/project/appdirs) for platform-agnostic file directories
 - [requests](https://requests.readthedocs.io) for HTTP page downloading
 - [beautifulsoup4](https://www.crummy.com/software/BeautifulSoup) for HTML parsing

All of them can be installed easily using `pip` or following instructions found on their websites.

### Installation

The easiest method is to place the [eventoftheday.py](eventoftheday.py) script somewhere on your systems path. For example, placing the script in `/usr/local/bin` lets you execute the script anywhere with `eventoftheday.py`. Better yet, renaming the script to `eventoftheday` means you can simply call `eventoftheday`.

Alternatively, you can specify the full path to the script when calling instead of placing it on your system's path. Below, it's assumed the script is on the system's path.

### Usage

Before any historic events can be printed, we first need to download the events by scraping Wikipedia's relevant articles:

```sh
$ eventoftheday download
```

This command may take a while, as each Wikipedia article, from `January_1` to `December_31`, has to be downloaded and parsed. The parsed events for each day are saved to disk.

Now with all the major historic events downloaded, we can use the following commands to print them:

```sh
$ eventoftheday events
```

By default, this will list out every historic event *that occurred on today's date*. To change which date to use, add the `-d` or `--date` argument:

```sh
$ eventoftheday events --date 05/01
```

This argument takes the format ***month/day***, so the above will print out all the major historic events that occurred on the 1st of May.

It's also possible to print a single historic event, picked at random:

```sh
$ eventoftheday random
$ eventoftheday random -d 12/8
```

The above prints two randomly chosen historic events: One occurred on today's date and the other occurred on the 8th of December.

Each command has it's own usage and help message, which can be found when `-h` or `--help` is specified.

```sh
$ eventoftheday -h
$ eventoftheday events --help
etc...
```

## References

Project idea found on [lainchan.org](https://lainchan.org) programming board.\
The Wikipedia articles for each day can be found [here](https://en.wikipedia.org/wiki/Category:Days).

[MIT License](LICENSE.md)

