# by Targosz Seweryn
# tseweryn@amazon.com

from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
import pandas as pd

from datetime import datetime, timedelta

from main_tools.widget_grabers import GrabWidget
from main_tools.selenium_scrap import GrabWeb


class FCLMRollupScrap:
    def __init__(self, start_date, end_date, driver=None, warehouse="KTW3", process_id="1003001"):
        self.start_date = start_date
        self.end_date = end_date
        # self.start_date = datetime.strptime(self.start_date, "%Y-%m-%d")
        # self.end_date = datetime.strptime(self.end_date, "%Y-%m-%d")
        if driver:
            self.driver = driver
        else:
            self.driver = GrabWeb.open_driver(GrabWidget.get_driver())
        self.warehouse = warehouse
        self.process_id = process_id
        self.delta = timedelta(days=1)
        self.rollup_df = pd.DataFrame()
        self.roster_df = pd.DataFrame()

    def get_roster(self):
        GrabWeb.get_web_site("https://fclm-portal.amazon.com/employee/employeeRoster?&warehouseId=KTW3")
        WebDriverWait(self.driver, timeout=1000).until(lambda d: d.find_element("id", "content-panel"))
        html = self.driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        my_table = soup.find(class_="sortable employeeList result-table")
        self.roster_df = pd.read_html(str(my_table))[0]
        self.roster_df.to_excel("arrm_scraper/roster.xlsx", sheet_name="result")

    def get_rollup(self):
        while self.start_date <= self.end_date:
            date_template = str(self.start_date).replace("-", "%2F")
            GrabWeb.get_web_site(f"https://fclm-portal.amazon.com/reports/functionRollup?reportFormat=HTML&warehouseId={self.warehouse}&processId={self.process_id}&spanType=Day&startDateDay={date_template.replace(' 00:00:00', '')}&maxIntradayDays=1&startHourIntraday=0&startMinuteIntraday=0&endHourIntraday=0&endMinuteIntraday=0")
            WebDriverWait(self.driver, timeout=1000).until(lambda d: d.find_element("id", "function-4300012734"))
            html = self.driver.page_source
            soup = BeautifulSoup(html, "html.parser")
            my_tables = soup.find_all(class_="sortable result-table align-left")
            for my_table in my_tables:
                df = pd.read_html(str(my_table), header=None, skiprows=1)[0]
                df = df.drop(df.columns[[col for col in range(len(df.columns)) if col > 3]], axis=1)
                #  df = df[["Type", "Id", "Name", "Manager"]]
                df.columns = ["Type", "Employee ID", "Employee Name", "Manager"]
                df = df[:-1]
                df = df.astype({"Employee ID": int}, errors='raise')
                if self.rollup_df.empty:
                    self.rollup_df = df.copy()
                else:
                    frame = [self.rollup_df, df]
                    self.rollup_df = pd.concat(frame, ignore_index=True)
            self.start_date += self.delta
        self.rollup_df = self.rollup_df.drop_duplicates(subset=["Employee ID"])
        self.rollup_df.to_excel("arrm_scraper/rollup.xlsx", sheet_name="result")

    def get_login_by_rollup(self):
        df_joined = pd.merge(self.rollup_df, self.roster_df, on="Employee ID")
        df_joined.to_excel("arrm_scraper/ppr.xlsx", sheet_name="result")
        return df_joined
