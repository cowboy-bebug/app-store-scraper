import random
import re


class Base:
    __scheme = "https"

    __landing_host = "apps.apple.com"
    __request_host = "amp-api.apps.apple.com"

    __landing_path = "{country}/app/{app_name}/id{app_id}"
    __request_path = "v1/catalog/{country}/apps/{app_id}/reviews"

    def __init__(self, country, app_name, app_id):
        self.country = str(country).lower()
        self.app_name = re.sub(r"[\W_]+", "-", str(app_name).lower())
        self.app_id = str(app_id)

        self.base_landing_url = f"{self.__scheme}://{self.__landing_host}"
        self.base_request_url = f"{self.__scheme}://{self.__request_host}"

        self.landing_url = self.__landing_url()
        self.request_url = self.__request_url()

        self.user_agents = [
            # NOTE: grab from https://bit.ly/2zu0cmU
            "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322)",
            "Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko",
            "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)",
        ]

        self.request_offset = 0
        self.request_headers = {
            "Accept": "application/json",
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Origin": self.base_landing_url,
            "Referer": self.landing_url,
            "User-Agent": random.choice(self.user_agents),
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

        self.log_timer = float()

    def __landing_url(self):
        landing_url = f"{self.__scheme}://{self.__landing_host}/{self.__landing_path}"
        return landing_url.format(
            country=self.country, app_name=self.app_name, app_id=self.app_id
        )

    def __request_url(self):
        request_url = f"{self.__scheme}://{self.__request_host}/{self.__request_path}"
        return request_url.format(country=self.country, app_id=self.app_id)
