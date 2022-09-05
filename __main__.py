# by Targosz Seweryn
# tseweryn@amazon.com


from selenium.common.exceptions import NoSuchWindowException

from arrm_scraper.arrm_by_station import ARRMScrap
from arrm_scraper.fclm_scrap_rollup import FCLMRollupScrap
from arrm_scraper.roboscout import RoboScout
from defect_logger.loggers import logger
from main_tools.df_tools import GrabDataframe
from main_tools.widget_grabers import GrabWidget
from main_tools.selenium_scrap import GrabWeb
from mm_feedback import Mastermind

import asyncio
import threading
import time
import traceback
from datetime import datetime, timedelta


class Main:
    @staticmethod
    def launcher():
        tool_box = GrabWidget.get_launcher()
        if tool_box == 'mm_feedback':
            Main.mm_feedback_launch()
        elif tool_box == 'bin_search':
            Main.bin_search_launch()
        elif tool_box == 'arrm_scraper':
            Main.arrm_scraper_launch()
        elif tool_box == 'kibana_scraper':
            Main.kibana_scraper_launch()

    @staticmethod
    def mm_feedback_launch():
        mastermind = Mastermind()
        mastermind.mm_prepare()
        try:
            submit = mastermind.mm_fill_submit
            complete = mastermind.mm_completion
            mastermind.mm_loop(submit, complete)
        except Exception:
            logger.error(traceback.format_exc())
        mastermind.mm_end()

    @staticmethod
    def bin_search_launch():
        pass

    @staticmethod
    def arrm_scraper_launch():
        threads = []
        delta = timedelta(days=1)
        start_date, end_date = GrabWidget.get_date_picker()
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        end_date = datetime.strptime(end_date, "%Y-%m-%d") + delta
        driver = GrabWeb.open_driver(GrabWidget.get_driver())
        arrm = ARRMScrap(start_date, end_date, driver=driver)
        arrm.arrm_midway()
        robo = RoboScout(start_date, end_date, driver)
        robo.active_pick_stations_load()
        stations_df = robo.active_pick_stations_scrap()
        for index, row in stations_df.iterrows():
            login_time = datetime.strptime(str(row['Time_In']), "%m/%d/%Y %H:%M:%S")
            active_time = timedelta(hours=float(row['Logged_Hours']))
            logout_time = login_time + active_time
            arrm.set_station(int(row['Station_Id']))
            t = threading.Thread(name=index, target=arrm.activity_by_station_load, args=(login_time, logout_time,))
            threads.append(t)
            if (index + 1) % 10 == 0:
                for x in threads:
                    print(f"{x} start")
                    x.start()
                for x in threads:
                    print(f"{x} join")
                    x.join()
                threads = []
                for e in range(1, 10):
                    parent = driver.window_handles[0]
                    chld = driver.window_handles[e]
                    driver.switch_to.window(chld)
                    time.sleep(0.5)
                    skip = arrm.activity_by_station_wait()
                    if not skip:
                        arrm.station_info_scrap(login_time, logout_time)
                for e in range(10):
                    print(f"{10 - e} close")
                    driver.switch_to.window(driver.window_handles[10 - e])
                    driver.close()
                driver.switch_to.window(driver.window_handles[0])
        arrm.arrm_end()

    @staticmethod
    def kibana_scraper_launch():
        threads = []
        delta = timedelta(days=1)
        start_date, end_date = GrabWidget.get_date_picker()
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        end_date = datetime.strptime(end_date, "%Y-%m-%d") + delta
        driver = GrabWeb.open_driver(GrabWidget.get_driver())
        arrm = ARRMScrap(start_date, end_date, driver=driver)
        arrm.arrm_midway()
        robo = RoboScout(start_date, end_date, driver)
        robo.active_pick_stations_load()
        stations_df = robo.active_pick_stations_scrap()
        for index, row in stations_df.iterrows():
            login_time = datetime.strptime(str(row['Time_In']), "%m/%d/%Y %H:%M:%S")
            active_time = timedelta(hours=float(row['Logged_Hours']))
            logout_time = login_time + active_time
            arrm.set_station(int(row['Station_Id']))
            t = threading.Thread(name=index, target=arrm.activity_by_station_load, args=(login_time, logout_time,))
            threads.append(t)
            if (index + 1) % 10 == 0:
                for x in threads:
                    print(f"{x} start")
                    x.start()
                for x in threads:
                    print(f"{x} join")
                    x.join()
                threads = []
                for e in range(1, 10):
                    parent = driver.window_handles[0]
                    chld = driver.window_handles[e]
                    driver.switch_to.window(chld)
                    time.sleep(0.5)
                    skip = arrm.activity_by_station_wait()
                    if not skip:
                        arrm.station_info_scrap(login_time, logout_time)
                for e in range(10):
                    print(f"{10 - e} close")
                    driver.switch_to.window(driver.window_handles[10 - e])
                    driver.close()
                driver.switch_to.window(driver.window_handles[0])
        arrm.arrm_end()

    @staticmethod
    def backup_arrm():
        delta = timedelta(days=1)
        start_date, end_date = GrabWidget.get_date_picker()
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        end_date = datetime.strptime(end_date, "%Y-%m-%d") + delta
        driver = GrabWeb.open_driver(GrabWidget.get_driver())
        arrm = ARRMScrap(start_date, end_date, driver=driver)
        arrm.arrm_midway()
        robo = RoboScout(start_date, end_date, driver)
        robo.active_pick_stations_load()
        stations_df = robo.active_pick_stations_scrap()
        for index, row in stations_df.iterrows():
            login_time = datetime.strptime(str(row['Time_In']), "%m/%d/%Y %H:%M:%S")
            active_time = timedelta(hours=float(row['Logged_Hours']))
            logout_time = login_time + active_time
            arrm.set_station(int(row['Station_Id']))
            arrm.activity_by_station_load(login_time, logout_time)
            html = arrm.get_html_src()
            arrm.station_info_scrap(login_time, logout_time, html)
        arrm.arrm_end()


if __name__ == '__main__':
    Main.launcher()
