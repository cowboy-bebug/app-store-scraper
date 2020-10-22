if __name__ == "__main__":
    from app_store_scraper import AppStore

    minecraft = AppStore(country="us", app_name="minecraft")
    minecraft.review()
