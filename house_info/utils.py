import logging
from typing import Tuple
import pandas as pd


logger = logging.getLogger(__name__)
DataFrame = pd.DataFrame
SHColumn = Tuple[int, str, str, str]


class PageList(list):
    def __str__(self):
        return f"1페이지부터 {len(self)}페이지까지 저장됨"

    def __repr__(self):
        return f"1페이지부터 {len(self)}페이지까지 저장됨"
