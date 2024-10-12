from typing import Optional

from selenium.webdriver.remote.webdriver import WebDriver


class SetupModel:
    def __init__(self):
        self.driver: Optional[WebDriver] = None
