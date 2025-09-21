from typing import Generator

from utils import TimeFormat

from scraper import AbstractPDFDoc
from utils_future import WWW


class TreasuryPressRelease(AbstractPDFDoc):
    URL_BASE = 'https://www.treasury.gov.lk'
    URL_PRESS_RELEASES = f'{URL_BASE}/web/press-releases'

    @classmethod
    def get_doc_class_label(cls) -> str:
        return 'lk_treasury_press_release'

    @classmethod
    def get_doc_class_description(cls) -> str:
        return "A Sri Lanka Treasury press release shares key govt financial updates—on budgets, debt, or policy—vital for transparency, guiding investors, citizens, and markets on the nation’s economic direction."  # noqa: E501

    @classmethod
    def get_doc_class_emoji(cls) -> str:
        return "💰"

    @classmethod
    def gen_docs_for_year(
        cls, year: str, url_for_year: str
    ) -> Generator[AbstractPDFDoc, None, None]:
        www = WWW(url_for_year)
        soup = www.soup
        assert soup
        table = soup.find('table', class_='MuiTable-root jss1')
        for tr in table.find_all('tr'):
            tds = tr.find_all('td')
            if len(tds) != 3:
                continue
            date_str_dd_mm_yyyy = tds[0].text.strip()
            date_str = TimeFormat.DATE.format(
                TimeFormat('%d-%m-%Y').parse(date_str_dd_mm_yyyy)
            )
            description = tds[1].text.strip()
            a = tds[2].find('a')
            url_pdf = f'{cls.URL_BASE}/{a.get("href")}'
            return cls(
                num=date_str,
                date_str=date_str,
                description=description,
                url_metadata=url_for_year,
                lang='en',
                url_pdf=url_pdf,
            )

    @classmethod
    def gen_years(cls) -> Generator[str, None, None]:
        www = WWW(cls.URL_PRESS_RELEASES)
        soup = www.soup
        assert soup
        div_nav = soup.find('div', class_='page-template--body__nav')
        assert div_nav
        ul = div_nav.find('ul')
        assert ul
        for li in ul.find_all('li'):
            a = li.find('a')
            assert a
            year = a.text.strip()
            assert year.isdigit() and len(year) == 4, year
            href = a.get('href')
            url = f'{cls.URL_BASE}/{href}'
            yield year, url

    @classmethod
    def gen_docs(cls) -> Generator[AbstractPDFDoc, None, None]:
        for year, url_year in cls.gen_years():
            yield from cls.gen_docs_for_year(year, url_year)
