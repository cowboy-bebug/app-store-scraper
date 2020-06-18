from app_store_scraper import AppStore

test_country = "Nz"
test_app_name = "Cool App"
test_app_id = 7357

app = AppStore(country=test_country, app_name=test_app_name, app_id=test_app_id)


def test_app_init_fields():
    assert app.country == test_country.lower()
    assert app.app_name == test_app_name.lower().replace(" ", "-")
    assert app.app_id == str(test_app_id).lower()


def test_app_urls():
    test_base_landing_url = "https://apps.apple.com"
    test_base_request_url = "https://amp-api.apps.apple.com"
    test_landing_path = f"{app.country}/app/{app.app_name}/id{app.app_id}"
    test_request_path = f"v1/catalog/{app.country}/apps/{app.app_id}/reviews"
    test_landing_url = f"{test_base_landing_url}/{test_landing_path}"
    test_request_url = f"{test_base_request_url}/{test_request_path}"

    assert app.landing_url == test_landing_url
    assert app.request_url == test_request_url


def test_app_defaults():
    assert app.log_interval == 10


def test_review():
    fortnite = AppStore(country="nz", app_name="fortnite", app_id=1261357853)
    fortnite.review(how_many=3)

    assert len(fortnite.reviews) == 20
    assert len(fortnite.reviews) == fortnite.reviews_count


def test_review_continuation():
    fortnite = AppStore(country="nz", app_name="fortnite", app_id=1261357853)

    fortnite.review(how_many=7)
    assert len(fortnite.reviews) == 20

    fortnite.review(how_many=5)
    assert len(fortnite.reviews) == 40

    for i in range(len(fortnite.reviews) - 1):
        assert fortnite.reviews[i] != fortnite.reviews[i + 1]
