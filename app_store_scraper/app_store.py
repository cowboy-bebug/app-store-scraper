import logging
from .base import Base

logger = logging.getLogger("AppStore")


class AppStore(Base):
    _landing_host = "apps.apple.com"
    _request_host = "amp-api.apps.apple.com"

    _landing_path = "{country}/app/{app_name}/id{app_id}"
    _request_path = "v1/catalog/{country}/apps/{app_id}/reviews"

    def __init__(
        self,
        country,
        app_name,
        app_id=None,
        log_format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        log_level="INFO",
        log_interval=5,
    ):
        super().__init__(
            country=country,
            app_name=app_name,
            app_id=app_id,
            log_format=log_format,
            log_level=log_level,
            log_interval=log_interval,
        )

        # override
        self._request_params = {
            "l": "en-GB",
            "offset": self._request_offset,
            "limit": 20,
            "platform": "web",
            "additionalPlatforms": "appletv,ipad,iphone,mac",
        }
