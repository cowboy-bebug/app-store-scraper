import logging
import re
import requests
import sys
import time
from datetime import datetime
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from .base import Base

logger = logging.getLogger("AppStore")


class AppStore(Base):
    def __init__(
        self,
        country,
        app_name,
        app_id,
        log_format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        log_level="INFO",
        log_interval=10,
    ):
        super().__init__(country, app_name, app_id)
        self.request_headers.update({"Authorization": self.__token()})

        logging.basicConfig(format=log_format, level=log_level.upper())
        self.log_interval = log_interval

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
            s.mount(self.base_request_url, HTTPAdapter(max_retries=retries))
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
