from app_store_scraper import AppStore, Podcast
from datetime import datetime, timedelta


class TestEmptyApp:
    country = "Nz"
    app_name = "Cool App"
    app_id = 7357
    app = AppStore(country=country, app_name=app_name, app_id=app_id)

    def test_init_attributes(self):
        assert self.app.country == self.country.lower()
        assert self.app.app_name == self.app_name.lower().replace(" ", "-")
        assert self.app.app_id == self.app_id
        assert self.app.reviews == []
        assert self.app.reviews_count == 0

    def test_init_url(self):
        base_landing_url = "https://apps.apple.com"
        landing_path = f"{self.app.country}/app/{self.app.app_name}/id{self.app.app_id}"
        landing_url = f"{base_landing_url}/{landing_path}"
        assert self.app.url == landing_url

    def test_repr(self):
        assert self.app.__repr__() == (
            f"AppStore(country='{self.app.country}', "
            f"app_name='{self.app.app_name}', "
            f"app_id={self.app.app_id})"
        )

    def test_str(self, capsys):
        print(self.app)
        captured = capsys.readouterr()
        assert captured.out == (
            f"     Country | {self.app.country}\n"
            f"        Name | {self.app.app_name}\n"
            f"          ID | {self.app.app_id}\n"
            f"         URL | {self.app.url}\n"
            f"Review count | {self.app.reviews_count}\n"
        )


class TestAppStore:
    app = AppStore(country="us", app_name="minecraft")

    def test_search_id(self):
        self.app.search_id()
        assert self.app.app_id == 479516143

    def test_review(self):
        self.app.review(how_many=3)
        assert len(self.app.reviews) == 20
        assert len(self.app.reviews) == self.app.reviews_count

    def test_review_continuation(self):
        assert len(self.app.reviews) == 20
        self.app.review(how_many=7)
        assert len(self.app.reviews) == 40

    def test_reviews_for_duplicates(self):
        for i in range(len(self.app.reviews) - 1):
            assert self.app.reviews[i] != self.app.reviews[i + 1]

    def test_reviews_for_after(self):
        t1 = datetime.now()
        t0 = t1 - timedelta(weeks=26)
        self.app.reviews = []
        self.app.review(how_many=3, after=t0)
        for review in self.app.reviews:
            assert review["date"] >= t0 and review["date"] < t1

    def test_reviews_for_sleep(self):
        t_start = datetime.now()
        self.app.review(how_many=40, sleep=2)
        t_diff = datetime.now() - t_start
        assert t_diff.seconds >= 2


class TestPodcast:
    podcast = Podcast(country="us", app_name="stuff you should know")

    def test_search_id(self):
        self.podcast.search_id()
        assert self.podcast.app_id == 278981407

    def test_review(self):
        self.podcast.review(how_many=3)
        assert len(self.podcast.reviews) == 20
        assert len(self.podcast.reviews) == self.podcast.reviews_count

    def test_review_continuation(self):
        assert len(self.podcast.reviews) == 20
        self.podcast.review(how_many=7)
        assert len(self.podcast.reviews) == 40

    def test_reviews_for_duplicates(self):
        for i in range(len(self.podcast.reviews) - 1):
            assert self.podcast.reviews[i] != self.podcast.reviews[i + 1]

    def test_reviews_for_after(self):
        t1 = datetime.now()
        t0 = t1 - timedelta(weeks=26)
        self.podcast.reviews = []
        self.podcast.review(how_many=3, after=t0)
        for review in self.podcast.reviews:
            assert review["date"] >= t0 and review["date"] < t1

    def test_reviews_for_sleep(self):
        t_start = datetime.now()
        self.podcast.review(how_many=40, sleep=2)
        t_diff = datetime.now() - t_start
        assert t_diff.seconds >= 2
