import logging
import random
import re
import requests
import sys
import time
from datetime import datetime
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

logger = logging.getLogger("Base")


class Base:
    _scheme = "https"

    _landing_host = ""
    _request_host = ""

    _landing_path = ""
    _request_path = ""

    _user_agents = [
        # NOTE: grab from https://bit.ly/2zu0cmU
        "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322)",
        "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko",
        "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)",
    ]

    def __init__(
        self,
        country,
        app_name,
        app_id=None,
        log_format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        log_level="INFO",
        log_interval=5,
    ):
        logging.basicConfig(format=log_format, level=log_level.upper())
        self._base_landing_url = f"{self._scheme}://{self._landing_host}"
        self._base_request_url = f"{self._scheme}://{self._request_host}"

        self.country = str(country).lower()
        self.app_name = re.sub(r"[\W_]+", "-", str(app_name).lower())
        if app_id is None:
            logger.info("Searching for app id")
            app_id = self.search_id()
        self.app_id = int(app_id)

        self.url = self._landing_url()

        self.reviews = list()
        self.reviews_count = int()

        self._log_interval = float(log_interval)
        self._log_timer = float()

        self._fetched_count = int()

        self._request_url = self._request_url()
        self._request_offset = 0
        self._request_headers = {
            "Accept": "application/json",
            "Authorization": self._token(),
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Origin": self._base_landing_url,
            "Referer": self.url,
            "User-Agent": random.choice(self._user_agents),
        }
        self._request_params = {}
        self._response = requests.Response()

        logger.info(
            f"Initialised: {self.__class__.__name__}"
            f"('{self.country}', '{self.app_name}', {self.app_id})"
        )
        logger.info(f"Ready to fetch reviews from: {self.url}")

    def __repr__(self):
        return "{}(country='{}', app_name='{}', app_id={})".format(
            self.__class__.__name__,
            self.country,
            self.app_name,
            self.app_id,
        )

    def __str__(self):
        width = 12
        return (
            f"{'Country'.rjust(width, ' ')} | {self.country}\n"
            f"{'Name'.rjust(width, ' ')} | {self.app_name}\n"
            f"{'ID'.rjust(width, ' ')} | {self.app_id}\n"
            f"{'URL'.rjust(width, ' ')} | {self.url}\n"
            f"{'Review count'.rjust(width, ' ')} | {self.reviews_count}"
        )

    def _landing_url(self):
        landing_url = f"{self._base_landing_url}/{self._landing_path}"
        return landing_url.format(
            country=self.country, app_name=self.app_name, app_id=self.app_id
        )

    def _request_url(self):
        request_url = f"{self._base_request_url}/{self._request_path}"
        return request_url.format(country=self.country, app_id=self.app_id)

    def _get(
        self,
        url,
        headers=None,
        params=None,
        total=3,
        backoff_factor=3,
        status_forcelist=[404, 429],
    ) -> requests.Response:
        retries = Retry(
            total=total,
            backoff_factor=backoff_factor,
            status_forcelist=status_forcelist,
        )
        with requests.Session() as s:
            s.mount(self._base_request_url, HTTPAdapter(max_retries=retries))
            logger.debug(f"Making a GET request: {url}")
            self._response = s.get(url, headers=headers, params=params)

    def _token(self):
        self._get(self.url)
        tags = self._response.text.splitlines()
        for tag in tags:
            if re.match(r"<meta.+web-experience-app/config/environment", tag):
                token = re.search(r"token%22%3A%22(.+?)%22", tag).group(1)
                return f"bearer {token}"

    def _parse_data(self, after):
        response = self._response.json()
        for data in response["data"]:
            review = data["attributes"]
            review["date"] = datetime.strptime(review["date"], "%Y-%m-%dT%H:%M:%SZ")
            if after and review["date"] < after:
                continue
            self.reviews.append(review)
            self.reviews_count += 1
            self._fetched_count += 1
            logger.debug(f"Fetched {self.reviews_count} review(s)")

    def _parse_next(self):
        response = self._response.json()
        next_offset = response.get("next")
        if next_offset is None:
            self._request_offset = None
        else:
            offset = re.search("^.+offset=([0-9]+).*$", next_offset).group(1)
            self._request_offset = int(offset)
            self._request_params.update({"offset": self._request_offset})

    def _log_status(self):
        logger.info(
            f"[id:{self.app_id}] Fetched {self._fetched_count} reviews "
            f"({self.reviews_count} fetched in total)"
        )

    def _heartbeat(self):
        interval = self._log_interval
        if self._log_timer == 0:
            self._log_timer = time.time()
        if time.time() - self._log_timer > interval:
            self._log_status()
            self._log_timer = 0

    def search_id(self):
        search_url = "https://www.google.com/search"
        self._get(search_url, params={"q": f"app store {self.app_name}"})
        pattern = fr"{self._base_landing_url}/[a-z]{{2}}/.+?/id([0-9]+)"
        app_id = re.search(pattern, self._response.text).group(1)
        return app_id

    def review(self, how_many=sys.maxsize, after=None, sleep=None):
        self._log_timer = 0
        if after and not isinstance(after, datetime):
            raise SystemExit("`after` must be a datetime object.")

        try:
            while True:
                self._heartbeat()
                self._get(
                    self._request_url,
                    headers=self._request_headers,
                    params=self._request_params,
                )
                self._parse_data(after)
                self._parse_next()
                if self._request_offset is None or self._fetched_count >= how_many:
                    break
                if sleep and type(sleep) is int:
                    time.sleep(sleep)
        except KeyboardInterrupt:
            logger.error("Keyboard interrupted")
        except Exception as e:
            logger.error(f"Something went wrong: {e}")
        finally:
            self._log_status()
            self._fetched_count = 0
