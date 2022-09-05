# by Targosz Seweryn
# tseweryn@amazon.com

from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup
import pandas as pd

import time
from datetime import timedelta

from main_tools.widget_grabers import GrabWidget
from main_tools.selenium_scrap import GrabWeb


class ARRMScrap:
    floor = ""
    station = ""
    task3 = None
    table_xpath = "/html/body/div[1]/div[2]/div/table/tbody/tr[1]"
    df_combined = pd.DataFrame()
    df_stations = pd.DataFrame()
    delta = timedelta(hours=4)

    def __init__(self, start_date, end_date, driver=None, warehouse="KTW3", customer="AMZN"):
        self.start_date = start_date
        self.end_date = end_date
        self.break_data = self.start_date + self.delta
        self.default_start = self.start_date
        self.default_end = self.end_date
        self.default_break = self.break_data
        if driver:
            self.driver = driver
        else:
            self.driver = GrabWeb.open_driver(GrabWidget.get_driver())
        self.warehouse = warehouse
        self.customer = customer

    def arrm_midway(self):
        GrabWeb.get_web_site("https://arrm-portal-eu-dub.dub.proxy.amazon.com/")
        WebDriverWait(self.driver, timeout=1000).until(lambda d: d.find_element("id", "navRightDiv"))

    @classmethod
    def session_by_user_scrap(cls, html):
        soup = BeautifulSoup(html, "html.parser")
        my_table = soup.find(id="items")
        df = pd.read_html(str(my_table))[0]
        if cls.df_stations.empty:
            cls.df_stations = df.copy()
        else:
            frame = [cls.df_stations, df]
            cls.df_stations = pd.concat(frame)

    def session_by_user_load(self, df_ppr):
        delta = timedelta(days=1)
        start_template = self.start_date.strftime(f"%Y-%m-%dT%H")
        link_end_date = self.end_date + delta
        end_template = link_end_date.strftime(f"%Y-%m-%dT%H")
        for user_id in df_ppr['User ID']:
            arrm = f"https://arrm-portal-eu-dub.dub.proxy.amazon.com/edw/sessions-by-user?customer={self.customer}&warehouse={self.warehouse}&zone=&timeRangeType=fixed&timeStart=2022-08-07T00%3A00&duration=72%3A00&timeEnd=2022-08-10T00%3A00&relativeStart=370%3A13&relativeEnd=298%3A13&timeRange={start_template}%3A00+-+{end_template}%3A00&user={user_id}&autoQuery=true"
            GrabWeb.get_web_site(arrm)
            time.sleep(1)
            html = GrabWeb.get_html_src()
            ARRMScrap.session_by_user_scrap(html)
        self.df_stations.to_excel("arrm_scraper/stations.xlsx", sheet_name="result")

    @classmethod
    def set_station(cls, station):
        cls.station = station
        if 2000 <= station < 3000:
            cls.floor = "2"
        elif 3000 <= station < 4000:
            cls.floor = "3"
        elif 4000 <= station < 5000:
            cls.floor = "4"

    def activity_by_station_load(self, start, end):
        start_template = str(start.strftime(f"%Y-%m-%dT%H:%M")).replace(":", "%3A")
        break_template = str(end.strftime(f"%Y-%m-%dT%H:%M")).replace(":", "%3A")
        print(f"{start_template} - {break_template}")
        arrm = f"https://arrm-portal-eu-dub.dub.proxy.amazon.com/edw/user-activities-by-station?customer={self.customer}&warehouse={self.warehouse}&zone=paKivaA0{self.floor}&timeRangeType=fixed&timeStart={start_template}&duration=04%3A00&timeEnd={break_template}&relativeStart=184%3A25&relativeEnd=180%3A25&timeRange={start_template}+-+{break_template}&station={self.station}&autoQuery=true"
        GrabWeb.create_threaded_tab(arrm)
        return start_template, break_template

    def activity_by_station_wait(self, wait_time=120):
        skip = False
        try:
            # todo wait find_element start date - end date .text if it's = self.start/end check entries value if 0 skip
            WebDriverWait(self.driver, timeout=wait_time).until(lambda d: d.find_element('id', 'items'))
            text_area = WebDriverWait(self.driver, timeout=wait_time).until(lambda d: d.find_element('class name', 'badge'))
            # WebDriverWait(self.driver, timeout=60).until(lambda d: d.find_element("xpath", self.table_xpath))
        except TimeoutException:
            try:
                self.driver.find_element("id", "auth-container")
            except NoSuchElementException:
                pass
            else:
                try:
                    WebDriverWait(self.driver, timeout=85000).until(lambda d: d.find_element("xpath", self.table_xpath))
                except TimeoutException:
                    self.driver.close()
        else:
            if int(text_area.text) == 0:
                skip = True
            else:
                skip = False
        return skip

    def get_html_src(self):
        html = self.driver.page_source
        return html

    def station_info_scrap(self, start_template, break_template):
        html = self.driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        my_table = soup.find(id="items")
        df = pd.read_html(str(my_table))[0]
        entries = soup.find(class_="badge")
        df = df.loc[df["ActualDuration"] == 0]
        df["SEARCH START"] = start_template
        df["SEARCH END"] = break_template
        df["FOUND ENTRIES"] = entries.text
        if self.df_combined.empty:
            self.df_combined = df.copy()
        else:
            frame = [self.df_combined, df]
            self.df_combined = pd.concat(frame)

    def arrm_end(self):
        self.driver.close()
        self.df_combined.to_excel("arrm_scraper/user_activity.xlsx", sheet_name="result", index=False)
