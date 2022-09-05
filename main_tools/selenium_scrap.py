# by Targosz Seweryn
# tseweryn@amazon.com

import threading

from selenium.webdriver import Firefox, Chrome
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException

from defect_logger.loggers import defect_logger


class GrabWeb:
    driver = None
    service = None

    @classmethod
    @defect_logger
    def open_driver(cls, ch_driver):

        if ch_driver == 'Firefox':
            cls.service = FirefoxService('main_tools/drivers/geckodriver.exe')
            cls.driver = Firefox(service=cls.service)
        elif ch_driver == 'Chrome':
            cls.service = ChromeService('main_tools/drivers/chromedriver.exe')
            cls.driver = Chrome(service=cls.service)
        return cls.driver

    @classmethod
    @defect_logger
    def get_web_site(cls, site_link):
        cls.driver.get(site_link)

    @classmethod
    @defect_logger
    def fill_text_area(cls, entry_value, el_type, el_name, type_enter=False):
        text_area = WebDriverWait(cls.driver, timeout=10).until(lambda d: d.find_element(el_type, el_name))
        text_area.send_keys(entry_value)
        if type_enter:
            text_area.send_keys(Keys.RETURN)

    @staticmethod
    @defect_logger
    def fill_specified_area(entry_value, el_type, el_name, spl_el, type_enter=False):
        text_area = WebDriverWait(spl_el, timeout=10).until(lambda d: d.find_element(el_type, el_name))
        text_area.send_keys(entry_value)
        if type_enter:
            text_area.send_keys(Keys.RETURN)

    @classmethod
    def check_exists(cls, el_type, el_name):
        try:
            cls.driver.find_element(el_type, el_name)
        except NoSuchElementException:
            return False
        return True

    @classmethod
    def get_html_src(cls):
        html = cls.driver.page_source
        return html

    @classmethod
    def create_threaded_tab(cls, url):
        print(threading.currentThread().getName(), 'Thread')
        print(url)
        cls.driver.execute_script("window.open('{0}')".format(url))
