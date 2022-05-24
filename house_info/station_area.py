import time
from typing import Final
from bs4 import BeautifulSoup, ResultSet
import pandas as pd
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from house_info.utils import DataFrame


# TODO: typing needed
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

    def __call__(self):
        return self.create_post_list_sources()


class StationAreaTable:
    def __init__(self, page_sources):
        self.page_sources = page_sources

    def get_data(self):
        index, _type, title, registration_date, subscription_date, manager = (
            [],
            [],
            [],
            [],
            [],
            [],
        )

        for page_source in self.page_sources:
            for post in page_source:
                items = post.find_all("td")
                index.append(items.pop(0).get_text().strip())
                _type.append(items.pop(0).get_text().strip())
                title.append(items.pop(0).get_text().strip())
                registration_date.append(items.pop(0).get_text().strip())
                subscription_date.append(items.pop(0).get_text().strip())
                manager.append(items.pop(0).get_text().strip())
        return index, _type, title, registration_date, subscription_date, manager

    def get_data_dict(self):
        data = self.get_data()
        data_dict = {
            "인덱스": data[0],
            "유형": data[1],
            "제목": data[2],
            "게시일": data[3],
            "청약신청일": data[4],
            "담당자": data[5],
        }
        return data_dict

    def create_data_frame(self):
        data_dict = self.get_data_dict()
        data_frame = pd.DataFrame(data=data_dict)
        return data_frame


class StationAreaDataManager:
    def __init__(self, chrome_driver_path: str, page: int = 1) -> None:
        self.request = StationAreaRequest(chrome_driver_path, page)

    def create_page_sources(self) -> ResultSet:
        page_sources = self.request()
        return page_sources

    def get_data_frame(self, page_sources) -> DataFrame:
        data_table = StationAreaTable(page_sources)
        data_table = data_table.create_data_frame()
        return data_table

    def export_csv(self, path: str) -> None:
        page_sources = self.create_page_sources()
        data_table = self.get_data_frame(page_sources)

        data_table.to_csv(path, index=False)
