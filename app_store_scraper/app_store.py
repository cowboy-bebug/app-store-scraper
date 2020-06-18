import logging
import random
import re
import requests
import sys
import time
from datetime import datetime
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

logger = logging.getLogger("AppStore")


class AppStore:
    __scheme = "https"

    __landing_host = "apps.apple.com"
    __request_host = "amp-api.apps.apple.com"

    __landing_path = "{country}/app/{app_name}/id{app_id}"
    __request_path = "v1/catalog/{country}/apps/{app_id}/reviews"

    __base_landing_url = f"{__scheme}://{__landing_host}"
    __base_request_url = f"{__scheme}://{__request_host}"

    __user_agents = [
        # NOTE: grab from https://bit.ly/2zu0cmU
        "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322)",
        "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko",
        "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)",
    ]

    def __init__(
        self,
        country,
        app_name,
        app_id,
        log_format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        log_level="INFO",
        log_interval=10,
    ):
        self.country = str(country).lower()
        self.app_name = re.sub(r"[\W_]+", "-", str(app_name).lower())
        self.app_id = str(app_id)

        self.landing_url = self.__landing_url()
        self.request_url = self.__request_url()

        self.request_offset = 0
        self.request_headers = {
            "Accept": "application/json",
            "Authorization": self.__token(),
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Origin": self.__base_landing_url,
            "Referer": self.landing_url,
            "User-Agent": random.choice(self.__user_agents),
        }
        self.request_params = {
            "l": "en-GB",
            "offset": self.request_offset,
            "limit": 20,
            "platform": "web",
            "additionalPlatforms": "appletv,ipad,iphone,mac",
        }

        self.reviews = list()
        self.reviews_count = int()
        self.fetched_count = int()

        logging.basicConfig(format=log_format, level=log_level.upper())
        self.log_interval = log_interval
        self.log_timer = float()

    def __repr__(self):
        return "{object}(country={country}, app_name={app_name}, app_id={app_id})".format(
            object=self.__class__.__name__,
            country=self.country,
            app_name=self.app_name,
            app_id=self.app_id,
        )

    def __str__(self):
        width = 12
        return (
            f"{'Country'.rjust(width, ' ')} | {self.country}\n"
            f"{'Name'.rjust(width, ' ')} | {self.app_name}\n"
            f"{'ID'.rjust(width, ' ')} | {self.app_id}\n"
            f"{'URL'.rjust(width, ' ')} | {self.landing_url}\n"
            f"{'Review count'.rjust(width, ' ')} | {self.reviews_count}"
        )

    def __landing_url(self):
        landing_url = f"{self.__base_landing_url}/{self.__landing_path}"
        return landing_url.format(
            country=self.country, app_name=self.app_name, app_id=self.app_id
        )

    def __request_url(self):
        request_url = f"{self.__base_request_url}/{self.__request_path}"
        return request_url.format(country=self.country, app_id=self.app_id)

    def __get(
        self,
        url,
        headers=None,
        params=None,
        total=3,
        backoff_factor=3,
        status_forcelist=[404],
    ) -> requests.Response:
        retries = Retry(
            total=total,
            backoff_factor=backoff_factor,
            status_forcelist=status_forcelist,
        )
        with requests.Session() as s:
            s.mount(self.__base_request_url, HTTPAdapter(max_retries=retries))
            logger.debug(f"Making a GET request: {url}")
            self.response = s.get(url, headers=headers, params=params)

    def __token(self):
        self.__get(self.landing_url)
        tags = self.response.text.splitlines()
        for tag in tags:
            if re.match(r"<meta.+web-experience-app/config/environment", tag):
                token = re.search(r"token%22%3A%22(.+?)%22", tag).group(1)
                return f"bearer {token}"

    def __parse_data(self):
        response = self.response.json()
        for data in response["data"]:
            review = data["attributes"]
            review["date"] = datetime.strptime(review["date"], "%Y-%m-%dT%H:%M:%SZ")
            self.reviews.append(review)
            self.reviews_count += 1
            self.fetched_count += 1
            logger.debug(f"Fetched {self.reviews_count} review(s)")

    def __parse_next(self):
        response = self.response.json()
        next_offset = response.get("next")
        if next_offset is None:
            self.request_offset = None
        else:
            offset = re.search("^.+offset=([0-9]+).*$", next_offset).group(1)
            self.request_offset = int(offset)
            self.request_params.update({"offset": self.request_offset})

    def __heartbeat(self):
        interval = self.log_interval
        if self.log_timer == 0:
            self.log_timer = time.time()
        if time.time() - self.log_timer > interval:
            logger.info(f"[{interval}s HEARTBEAT] Fetched {self.reviews_count} reviews")
            self.log_timer = 0

    def review(self, how_many=sys.maxsize):
        logger.info(f"Fetching reviews for {self.landing_url}")
        while True:
            self.__heartbeat()
            self.__get(
                self.request_url,
                headers=self.request_headers,
                params=self.request_params,
            )
            self.__parse_data()
            self.__parse_next()
            if self.request_offset is None or self.fetched_count >= how_many:
                logger.info(f"Fetched {self.fetched_count} reviews")
                self.fetched_count = 0
                break
