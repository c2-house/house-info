import time
from typing import Final
from bs4 import BeautifulSoup, ResultSet
import pandas as pd
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from house_info.utils import DataFrame


class MyHomeRequest:
    """
    마이홈 포털 정보 수집
    :ChromeDriver 필요
    """

    MYHOME_URL: Final = (
        "https://www.myhome.go.kr/hws/portal/sch/selectRsdtRcritNtcView.do"
    )

    def __init__(
        self,
        chrome_driver_path: str = "./chromedriver.exe",
        page: int = 1,
        types="student",
        region="seoul",
    ) -> None:
        self.__service = Service(chrome_driver_path)
        self.page = page
        self.types = types
        self.region = region

    def browser_open_headless(self):
        chrome_option = Options()
        chrome_option.add_argument("--headless")
        browser = Chrome(service=self.__service, options=chrome_option)
        browser.implicitly_wait(2)
        browser.get(MyHomeRequest.MYHOME_URL)
        return browser

    def get_page_source(self, browser):
        page_source = browser.page_source
        return page_source

    def get_post_list(self, soup):
        post_list = soup.find("tbody", attrs={"id": "schTbody"}).find_all("tr")
        if not post_list:
            return None
        return post_list

    def parse_html(self, page_source):
        soup = BeautifulSoup(page_source, "html.parser")
        return soup

    def move_next_page(self, browser, page):
        browser.execute_script(f"fnSearch({page})")
        return browser

    def click_category(self, browser):
        # 서울
        browser.execute_script("fnSchKoreaMapClick('11');")
        # 대학생
        browser.execute_script("setUserTy('FIXES100001');")
        return browser

    def create_post_list_sources(self):
        browser = self.browser_open_headless()
        click_category = self.click_category(browser)
        time.sleep(1)
        page_source = self.get_page_source(browser)
        parsed_html = self.parse_html(page_source)
        post_list = self.get_post_list(parsed_html)
        post_list_sources = [post_list]

        for page in range(2, self.page + 1):
            self.move_next_page(browser, page)
            time.sleep(0.1)
            # TODO: neeed to extract func
            page_source = self.get_page_source(browser)
            parsed_html = self.parse_html(page_source)
            post_list = self.get_post_list(parsed_html)

            if not post_list:
                break
            post_list_sources.append(post_list)
        browser.close()
        return post_list_sources
