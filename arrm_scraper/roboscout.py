# by Targosz Seweryn
# tseweryn@amazon.com

from main_tools.selenium_scrap import GrabWeb
from main_tools.widget_grabers import GrabWidget

from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
import pandas as pd


class RoboScout:
    def __init__(self, start_date, end_date, driver=None, warehouse="KTW3"):
        if driver:
            self.driver = driver
        else:
            self.driver = GrabWeb.open_driver(GrabWidget.get_driver())
        self.start_date = start_date
        self.end_date = end_date
        self.warehouse = warehouse

    def active_pick_stations_load(self):
        start_date = self.start_date.strftime(f"%Y-%m-%d")
        end_date = self.end_date.strftime(f"%Y-%m-%d")
        GrabWeb.get_web_site(
            f"https://roboscout.amazon.com/analyze/20711/?&sites=({self.warehouse})&datasource_startDateTime={start_date}%2004:30:00&datasource_endDateTime={end_date}%2015:00:00&mom_ids=1582&osm_ids=&oxm_ids=643%2C1429&ofm_ids=643&datasource_viz=nvd3Table")
        WebDriverWait(self.driver, timeout=45).until(
            lambda d: d.find_element("xpath", "/html/body/div[2]/div[4]/div[1]/div/div[2]/div/table/thead/tr/td[1]"))

    @staticmethod
    def active_pick_stations_scrap():
        html = GrabWeb.get_html_src()
        soup = BeautifulSoup(html, "html.parser")
        table = soup.find(class_="sortable table table-bordered table-fancybox table-condensed")
        df = pd.read_html(str(table))[0]
        df.to_excel("new.xlsx", sheet_name="result", index=False)
        return df






