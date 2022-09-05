from selenium.common.exceptions import NoSuchWindowException

from main_tools.df_tools import GrabDataframe
from main_tools.widget_grabers import GrabWidget
from main_tools.selenium_scrap import GrabWeb
from mm_feedback import Mastermind
from defect_logger.loggers import logger
from arrm_scraper.arrm_by_station import ARRMScrap
from arrm_scraper.fclm_scrap_rollup import FCLMRollupScrap
from arrm_scraper.roboscout import RoboScout

from selenium.webdriver.support.ui import WebDriverWait

import pickle
import time
import numpy as np
import asyncio
import multiprocessing
import threading
import traceback
from datetime import datetime, timedelta


import os.path
import pickle
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def save_cookies():
    print("Saving cookies in " + selenium_cookie_file)
    pickle.dump(driver.get_cookies() , open(selenium_cookie_file,"wb"))

def load_cookies():
    if os.path.exists(selenium_cookie_file) and os.path.isfile(selenium_cookie_file):
        print("Loading cookies from " + selenium_cookie_file)
        cookies = pickle.load(open(selenium_cookie_file, "rb"))

        # Enables network tracking so we may use Network.setCookie method
        driver.execute_cdp_cmd('Network.enable', {})

        # Iterate through pickle dict and add all the cookies
        for cookie in cookies:
            # Fix issue Chrome exports 'expiry' key but expects 'expire' on import
            if 'expiry' in cookie:
                cookie['expires'] = cookie['expiry']
                del cookie['expiry']

            # Replace domain 'apple.com' with 'microsoft.com' cookies
            cookie['domain'] = cookie['domain'].replace('register.midway-auth.amazon.com', 'https://midway-auth.amazon.com/login?next=%2F')
            cookie['domain'] = cookie['domain'].replace('midway-auth.amazon.com', 'https://midway-auth.amazon.com/login?next=%2F')

            # Set the actual cookie
            driver.execute_cdp_cmd('Network.setCookie', cookie)

        # Disable network tracking
        driver.execute_cdp_cmd('Network.disable', {})
        return 1

    print("Cookie file " + selenium_cookie_file + " does not exist.")
    return 0

def pretty_print(pdict):
    for p in pdict:
        print(str(p))
    print('',end = "\n\n")


# Minimal settings
selenium_cookie_file = 'test.txt'

# browser_options = Options()
# browser_options.add_argument("--headless")

# Open a driver, get a page, save cookies
# driver = webdriver.Chrome(chrome_options=browser_options)
driver = GrabWeb.open_driver(GrabWidget.get_driver())
driver.get('https://midway.amazon.com/')
WebDriverWait(driver, timeout=1000).until(lambda d: d.find_element("id", "tokens-pane"))
save_cookies()
pretty_print(driver.get_cookies())


# Rewrite driver with a new one, load and set cookies before any requests
# driver = webdriver.Chrome(chrome_options=browser_options)
driver = GrabWeb.open_driver(GrabWidget.get_driver())
load_cookies()
driver.get('https://midway.amazon.com/')
pretty_print(driver.get_cookies())


def cpu_split_df():
    cpu_count = multiprocessing.cpu_count()
    print(cpu_count)

    df = GrabDataframe.get_df_excel(GrabWidget.get_path())

    split_df = np.array_split(df, cpu_count)
    for split in split_df:
        print(split)


def arrm_scraper_launch():
    threads = []
    delta_day = timedelta(days=1)
    delta_hour = timedelta(hours=2)
    start_date, end_date = GrabWidget.get_date_picker()
    start_date = datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.strptime(end_date, "%Y-%m-%d") + delta_day
    driver = GrabWeb.open_driver(GrabWidget.get_driver())
    arrm = ARRMScrap(start_date, end_date, driver=driver)
    arrm.arrm_midway()
    robo = RoboScout(start_date, end_date, driver)
    robo.active_pick_stations_load()
    stations_df = robo.active_pick_stations_scrap()
    for index, row in stations_df.iterrows():
        login_time = datetime.strptime(str(row['Time_In']), "%m/%d/%Y %H:%M:%S")
        login_time -= delta_hour
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


driver = GrabWeb.open_driver(GrabWidget.get_driver())
driver.implicitly_wait(1)
GrabWeb.get_web_site("https://midway.amazon.com/")
# WebDriverWait(driver, timeout=1000).until(lambda d: d.find_element("id", "tokens-pane"))
# pickle.dump( driver.get_cookies(), open("cookies.pkl", "wb"))
# driver.close()


# driver = GrabWeb.open_driver(GrabWidget.get_driver())
# GrabWeb.get_web_site("https://midway.amazon.com/")
# time.sleep(2)
# driver.add_cookie({'name': 'amazon_enterprise_access', 'value': 'eyJhbGciOiJSUzI1NiIsImtpZCI6Ijg3WHRnMjhvQ2dpTVVxRHRmRU0xbjlDVU9pbyIsInR5cCI6IkpXVCJ9.eyJhbWF6b25fZW50ZXJwcmlzZV9hY2Nlc3MiOnRydWUsInN0YWNrIjoicHJvZCIsIm5iZiI6MTY2MjAyNzU3NywiaWF0IjoxNjYyMDI3ODc3LCJleHAiOjE2NjIwMjg3NzcsImp0aSI6ImZjNTJkMDRhLWEwOWYtZWM3Ni1mMDFiLTRjYTRhNzc1MGJmOCIsImRldmljZV9pZCI6IjUzMDdkNTM1LWVjYTEtNDkzNC05MTNmLWQ0ZDMyNDdlYTNiMiIsImxvZ2dlZF9pbl91c2VybmFtZSI6InRzZXdlcnluIiwic3lzdGVtX3R5cGUiOiJEZXNrdG9wIiwicGxhdGZvcm0iOiJXaW5kb3dzIiwiY2xhaW1zIjpbeyJHdWlkIjoiNWE2MDM4YzktNTQzYS01MDRiLTFkNDItZjEyYzQ3NDdmNWYzIiwibmFtZSI6ImNvbS5hbWF6b24uYWNtZS5jb21wbGlhbmNlIiwidHJ1c3R2YWx1ZSI6MS4wLCJkYXRlVGltZSI6IjIwMjItMDktMDFUMTA6MjQ6MzciLCJjYXBJbmZvIjp7ImNsYXNzIjoiY29tLmFtYXpvbi5hY21lIiwidmVyc2lvbiI6IjEuMC4wIn0sImNsaWVudENoYWluSW5mbyI6eyJkZXZpY2VJRCI6IjUzMDdkNTM1LWVjYTEtNDkzNC05MTNmLWQ0ZDMyNDdlYTNiMiJ9LCJjbGFpbXNJbmZvIjp7ImRhdGFDbGFpbXMiOnsiY29tcGxpYW5jZS5XaW5kb3dzIFVwZGF0ZS5zdGF0dXMiOjQsImNvbXBsaWFuY2UuV2luZG93cyBVcGRhdGUuY29uZmlnLmNhYi5zaGEyNTYiOiJlYzJkMGJjMzc2MWI1MzY4YWM4Y2YwN2YyYjM0MDE3MGVlZjBhNmY3YTc5NjA1OTgzMzhkMWNhOTI4YjFlOGU0IiwiY29tcGxpYW5jZS5XaW5kb3dzIFVwZGF0ZS5tYW5pZmVzdC5zaGEyNTYiOiI0OWI1YWJiM2JmMGRmMTBlYThiMTlkOWRmY2FlZWIxNTBkMzZkZTU0MmNlZjg4ZTlkNWEzODIyMzBkZmMzYWNkIiwiY29tcGxpYW5jZS5RdWFseXMuc3RhdHVzIjo0LCJjb21wbGlhbmNlLlF1YWx5cy5tYW5pZmVzdC5zaGEyNTYiOiJmNDZjODYxN2NkMWYyNTY5YzkzOTBmNDQ5ZjY0ZjkyYThhM2IxM2ZmZjc2ZTJlZThiYzJjMzllMTQyOWVjNGZhIiwiY29tcGxpYW5jZS5PUyBWZXJzaW9uLnN0YXR1cyI6NCwiY29tcGxpYW5jZS5PUyBWZXJzaW9uLm1hbmlmZXN0LnNoYTI1NiI6IjkxMzIzMTU2ZTJmZWRiODYxMmY4NTE2NjlmMDVmMzZjOWQyNjI5N2FlYWZjZGVjNmRmNjdjYWViZDBiYzRhN2QiLCJjb21wbGlhbmNlLk1hbmFnZW1lbnQuc3RhdHVzIjowLCJjb21wbGlhbmNlLkN5bGFuY2Uuc3RhdHVzIjo0LCJjb21wbGlhbmNlLlRoaXJkIFBhcnR5LnN0YXR1cyI6NCwiY29tcGxpYW5jZS5UaGlyZCBQYXJ0eS5tYW5pZmVzdC5zaGEyNTYiOiIzNWQ1Y2Q3NWVlMTZjYzRhOTliZWYxZGM0ZWE2MTUwZDE5NGNiNjhkMjY2ZTczNmYxNmMzM2FjYzliZGJjYjdmIiwiY29tcGxpYW5jZS5JbmZlY3Rpb24uc3RhdHVzIjo0LCJjb21wbGlhbmNlLkZpcmV3YWxsLnN0YXR1cyI6NCwiY29tcGxpYW5jZS5DcnlwdG8uc3RhdHVzIjo0LCJjb21wbGlhbmNlLk9mZmljZSBVcGRhdGUuc3RhdHVzIjo0LCJjb21wbGlhbmNlLk9mZmljZSBVcGRhdGUubWFuaWZlc3Quc2hhMjU2IjoiMzc5OGExYmU0NzY0Mjg3N2FmZGI1NjZiMzUyODM2MzZjMDgyZjEzYjUyYWNlY2UyOTI0OTc1YjY3ZDEyMDY4ZiJ9fX1dfQ.gmHIJ1NIDDSZnCuWAORtek_EA66QScp3J5bAe-O-BPpkR61k64e0rXdZ40flxcb47_SHoKymoSw2x382Gii-K2XV2TWDqIPEbMhNn0ciwVQ5RKbQnpEW6DHyLx5nd-MvEbZiZ-BX0l0k_PO2kmVIxnDcdXWHORS86duSwnZ5T-WuiM5oQTgicLqG2FOO33iK0zgoAgAGa6HrfxYFJmai7g0M4zQt8CzkpVnbTH5jk91wXTD6KqbvTQwlcLX38xCD9l9HonbQdqAQTQHsRJX3R2g_H-P-1MKOPDkBv_NOghRCIrjEUzlG6OgAQnSS5aSz8t_LHuSDefERkm-ll0hniA', 'path': '/', 'domain': 'midway-auth.amazon.com', 'secure': True, 'httpOnly': False, 'expiry': 1662028777, 'sameSite': 'None'})
# driver.add_cookie({'name': 'kerberos_disabled', 'value': '1', 'path': '/', 'domain': 'midway-auth.amazon.com', 'secure': True, 'httpOnly': False, 'expiry': 1693563879, 'sameSite': 'None'})
#driver.add_cookie({'name': 'aea_braveheart', 'value': '1', 'path': '/', 'domain': 'midway-auth.amazon.com', 'secure': True, 'httpOnly': False, 'expiry': 1693563879, 'sameSite': 'None'})
#driver.add_cookie({'name': 'user_name', 'value': 'tseweryn', 'path': '/', 'domain': 'midway-auth.amazon.com', 'secure': True, 'httpOnly': False, 'expiry': 1693563890, 'sameSite': 'None'})
#driver.add_cookie({'name': 'request_browser', 'value': '', 'path': '/', 'domain': 'midway-auth.amazon.com', 'secure': True, 'httpOnly': False, 'sameSite': 'None'})
#driver.add_cookie({'name': 'session', 'value': 'eyJraWQiOiIyMzMiLCJhbGciOiJkaXIiLCJlbmMiOiJBMTI4Q0JDLUhTMjU2In0..AQ017ApdbPWUKqA59C8lUQ.RVIISaXwDhYVulMs6HoHC3abnMdn_iNAMIz6bYqVZgqRIjYatUgY4YZnVzacNJCIGO1iS6XMGURDecc0ougoWtSFXoDKs7_GRNl8ts4DIGQ91w5YypG4NIog8eBTHZVdW6U45iVMwK6dGWTSdu6hD1cCuP6sINy0lH8lDv05WJllHpzJD4fP4ANeB33wNINujoF2UZlOrYXJ-kOZt5lBymY2aYTBhknQypqKk8SLUyUvMo-q79rrY2JOyPcrUhb4D6wLwSRH46MT-rJu3d_aLktBWZCSnS6Z6DtASN56nzFgkGWl60kqFb3_PnkiBwLTs67kDNlbabZ_6zConNVV3AyXXiH7_Jzpt-xBiyHTjrTcmnpEGu9rUhPC5Bo3Ez9QJce0tCgeKPWZpI_CILaGTQ5jh_GBJuAqioacs9YiZYSPdP0qGaz1JzH7N-ORB6JI3eAlMiissqjXRadwiji5kOdGZcG6nqupFUY1RZw16GvH13syrIgUVnp2VHHBRb7qd6RJtCaI4vx2i8SjdJ7n1g5N7GHSnXCl33a3sR5vKubVPyINRLCJcNTDWOaef9lEnJ-X8Q01sYnf9KBVRdhYo8Hxrqx4BhvfzObcIF99E4hB-RKPZXWbeF84VOvMOMAZN2dtSNSr7-hhV_sbK_2ps1gsdoDyAs8Z-qdVwdavnivvuij2jFGsrXVj2CFFGXokkZV8tJ9GVa_QX8wy6Gce7vuW2PqjH89garTmpUIAafpmIAfDs_zRDiD8bFXPSaf0y9hJAvXownvFcBKdrRC-oQ.pSVNZVEG9SbVUQ4sjnTA8w', 'path': '/', 'domain': 'midway-auth.amazon.com', 'secure': True, 'httpOnly': True, 'expiry': 1662099890, 'sameSite': 'None'})
#driver.add_cookie({'name': 'amzn_sso_token', 'value': 'eyJ0eXAiOiJKV1MiLCJhbGciOiJSUzI1NiIsImtpZCI6IjEwMDA2MDgzIn0.eyJpc3MiOiJodHRwczovL21pZHdheS1hdXRoLmFtYXpvbi5jb20iLCJzdWIiOiJ0c2V3ZXJ5biIsImF1ZCI6Imh0dHBzOi8vcmVnaXN0ZXIubWlkd2F5LWF1dGguYW1hem9uLmNvbTo0NDMiLCJleHAiOjE2NjIwMjg3OTMsImlhdCI6MTY2MjAyNzg5MywiYXV0aF90aW1lIjoxNjYyMDI3ODkwLCJub25jZSI6IjRkOThkZWFiNTc1NmEwMmFhZDk4OGY1NDNjOGM2MGRjNTUzZDM1MWMxOGM4OWExZjI3NjUxNDdmYjk1MDAzZTIiLCJhbXIiOiJbXCJwaW5cIiwgXCJ1MmZcIl0iLCJ0cnVzdF9zY29yZSI6bnVsbCwicmVxX2lkIjpudWxsLCJtaWR3YXlfdHJ1c3Rfc2NvcmUiOm51bGwsImFwZXNfcmVzdWx0cyI6bnVsbCwiaWFsIjowLCJhYWwiOjAsImp0aSI6IlVwWWdtZkVzKzdIVUp2b1QwVWpaTGc9PSIsInBvc3R1cmVfY2hlY2siOjAsIm13aSI6MH0.Bwfb7Up_k4TFqXCIxUI7TwwtfGsXhrGG8ZTYdrqUWcuHOWQ0wbd_XhO3HeZzoxL_TwS_ttGLdpARB8V4qmNxU6Il-T1xoBXx6YVo6k93LxDYzdknmget0NM0k42OTWCoP_xzLcKgZJIf4OP8hol0IusEPxaV8SVW__Y_V8hq_KNDdEXm7RPh33BOCSJApvt1AsObXNrq4aGdM4ETOqAEAjGVH7mtaDZL3CV6Rt9nOeL_N17jZUw2lho0Oelovvs7okCB6UYTeAm1x-uHlyRT7BkzNjyQb5Joj9IhfjgAKm8Pfu88Hqyh0X9tb0ceTO4w4iGqTQp5L37OGCCBEMh5XQ', 'path': '/', 'domain': 'register.midway-auth.amazon.com', 'secure': True, 'httpOnly': True, 'expiry': 1662028793, 'sameSite': 'None'})
#driver.add_cookie({'name': 'amzn_sso_rfp', 'value': '66ceada3e86f38b0', 'path': '/', 'domain': 'register.midway-auth.amazon.com', 'secure': True, 'httpOnly': True, 'expiry': 1662028793, 'sameSite': 'None'})
# driver.add_cookie({'name': '_rails-root_session', 'value': 'eHFFMHFYTUJJWmg4VjB4dDVoMzhDblRlZXFEUkcrTkVzQnNJeXFvS2FYT0JOQ3RvQ2VGSFRKRUVRQ2dEZTh2S1NTNW1QOUtORUE1TmJuOHQwT1BEK1YzWGl3WTAxS0gzRmFlSlBIYlJQUU14NDB0TzU0WU44VngwejRENE9IN0hhYlcxRXJLQzI2ZGlvZ0ZKcjA3bnBLWkVlclAxL0JuMFBGZWViVy9wT0V2ZFRoK3I1K0JKakhJTDM3eXVocnhXSXBkNWR2RFgvUUtNSXVqTGZZdk5VMjdLdTRZN09ORnZQdTByd0FZMUpHeFhleldrVUlBLzFYSWpiSGxkVWlSWUthdTB3Qk4xSWIxVUJMZHFucWV1RWd1UFNocGRRWHJxUllwMXpBRk01Y1NCaVRSSUlzZHYrOWVZcjY2Rm9vQTFDdTBtckFXaUFTZ04xcFA1bldTbURnPT0tLUZuWkNzaWtoSUZVaXhNdkgwR0xqU2c9PQ%3D%3D--d8d5ffbd98991f305e5a08d2ace8c0db22c6901f', 'path': '/', 'domain': 'register.midway-auth.amazon.com', 'secure': True, 'httpOnly': True, 'expiry': 1662099901, 'sameSite': 'None'})
# GrabWeb.get_web_site("https://arrm-portal-eu-dub.dub.proxy.amazon.com/")
# WebDriverWait(driver, timeout=1000).until(lambda d: d.find_element("id", "navRightDiv"))

