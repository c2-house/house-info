import time
from typing import Final
from bs4 import BeautifulSoup
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service


class StationAreaRequest:
    """
    역세권 청년주택 정보 수집
    민간, 공공 포함
    :ChromeDriver 필요
    """

    SA_URL: Final = "https://soco.seoul.go.kr/youth/bbs/BMSR00015/list.do?menuNo=400008"

    def __init__(
        self, chrome_driver_path: str = "./chromedriver.exe", page: int = 1
    ) -> None:
        self.__service = Service(chrome_driver_path)
        self.page = page

    def browser_open_headless(self):
        chrome_option = Options()
        chrome_option.add_argument("--headless")
        browser = Chrome(service=self.__service, options=chrome_option)
        browser.implicitly_wait(2)
        browser.get(StationAreaRequest.SA_URL)
        return browser

    def get_page_source(self, browser):
        page_source = browser.page_source
        return page_source

    def parse_html(self, page_source):
        soup = BeautifulSoup(page_source, "html.parser")
        return soup

    def get_post_list(self, soup):
        post_list = soup.find("tbody", attrs={"id": "boardList"}).find_all("tr")
        if not post_list:
            return None
        return post_list

    def move_next_page(self, browser, page):
        browser.execute_script(f"cohomeList({page})")
        return browser

    def create_post_list_sources(self):
        browser = self.browser_open_headless()
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
