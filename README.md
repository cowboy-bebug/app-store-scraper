![Build](https://github.com/cowboy-bebug/app-store-scraper/workflows/Build/badge.svg)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](https://github.com/cowboy-bebug/app-store-scraper/pulls)
<a href="https://github.com/psf/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>

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

fortnite = AppStore(country="nz", app_name="fortnite", app_id=1261357853)
fortnite.review(how_many=20)

pprint(fortnite.reviews)
pprint(fortnite.reviews_count)
```

# Extra Details

Let's continue from the code example used in [Quickstart](#quickstart).


## Instantiation

There are three required arguments, `country, app_name, app_id`.

```pycon
>>> fortnite
AppStore(country=nz, app_name=fortnite, app_id=1261357853)
```

These are required to create a URL for the App Store landing page, which can be displayed by the private field, `landing_url` like below:

```pycon
>>> fortnite.landing_url
'https://apps.apple.com/nz/app/fortnite/id1261357853'
```

There are optional arguments used to override log settings:

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
