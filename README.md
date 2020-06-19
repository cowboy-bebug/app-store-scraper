![build](https://img.shields.io/github/workflow/status/cowboy-bebug/app-store-scraper/Build)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/cowboy-bebug/app-store-scraper/pulls)
[![PyPI](https://img.shields.io/pypi/v/app-store-scraper)](https://pypi.org/project/app-store-scraper/)
![downloads](https://img.shields.io/pypi/dm/app-store-scraper)
![license](https://img.shields.io/pypi/l/app-store-scraper)
![code style](https://img.shields.io/badge/code%20style-black-black)

```
   ___                _____ _                   _____
  / _ \              /  ___| |                 /  ___|
 / /_\ \_ __  _ __   \ `--.| |_ ___  _ __ ___  \ `--.  ___ _ __ __ _ _ __   ___ _ __
 |  _  | '_ \| '_ \   `--. \ __/ _ \| '__/ _ \  `--. \/ __| '__/ _` | '_ \ / _ \ '__|
 | | | | |_) | |_) | /\__/ / || (_) | | |  __/ /\__/ / (__| | | (_| | |_) |  __/ |
 \_| |_/ .__/| .__/  \____/ \__\___/|_|  \___| \____/ \___|_|  \__,_| .__/ \___|_|
       | |   | |                                                    | |
       |_|   |_|                                                    |_|
```

# Quickstart

```console
pip3 install app-store-scraper
```

```python
from app_store_scraper import AppStore
from pprint import pprint

fortnite = AppStore(country="nz", app_name="fortnite")
fortnite.review(how_many=20)

pprint(fortnite.reviews)
pprint(fortnite.reviews_count)
```


# Extra Details

Let's continue from the code example used in [Quickstart](#quickstart).


## Instantiation

There are two required and one positional parameters:

- `country` (required)
  - two-letter country code of [ISO 3166-1 alpha-2](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2) standard
- `app_name` (required)
  - name of an iOS application to fetch reviews for
  - also used by `search_id()` method to search for `app_id` internally
- `app_id` (positional)
  - can be passed directly
  - or ignored to be obtained by `search_id` method internally

Once instantiated, the object can be examined:
```pycon
>>> fortnite
AppStore(country='nz', app_name='fortnite', app_id=1261357853)
```
```pycon
>>> print(app)
     Country | nz
        Name | fortnite
          ID | 1261357853
         URL | https://apps.apple.com/nz/app/fortnite/id1261357853
Review count | 0
```

Other optional parameters are:

- `log_format`
  - passed directly to `logging.basicConfig(format=log_format)`
  - default is `"%(asctime)s [%(levelname)s] %(name)s - %(message)s"`
- `log_level`
  - passed directly to `logging.basicConfig(level=log_level)`
  - default is `"INFO"`
- `log_interval`
  - log is produced every 10 seconds (by default) as a "heartbeat" (useful for a long scraping session)
  - default is `10`


## Fetching Review

The maximum number of reviews fetched per request is 20. To minimise the number of calls, the limit of 20 is hardcoded. This means the `review()` method will always grab more than the `how_many` argument supplied with an increment of 20.

```pycon
>>> fortnite.review(how_many=33)
>>> fortnite.reviews_count
40
```

If `how_many` is not provided, `review()` will terminate after *all* reviews are fetched.

**NOTE** the review count seen on the landing page differs from the actual number of reviews fetched. This is simply because only *some* users who rated the app also leave reviews.


## Review Data

The fetched review data are loaded in memory and live inside `reviews` attribute as a list of dict.
```pycon
>>> fortnite.reviews
[{'userName': 'someone', 'rating': 5, 'date': datetime.datetime(...
```

Each review dictionary has the following schema:
```python
{
    "date": datetime.datetime,
    "isEdited": bool,
    "rating": int,
    "review": str,
    "title": str,
    "userName": str
 }
```
