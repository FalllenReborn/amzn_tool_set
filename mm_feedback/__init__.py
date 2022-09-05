# by Targosz Seweryn
# tseweryn@amazon.com
import time

from defect_logger.loggers import logger
from main_tools.widget_grabers import GrabWidget
from main_tools.selenium_scrap import GrabWeb
from main_tools.df_tools import GrabDataframe
from mm_feedback.site_dicts import site_dict, type_dict

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait


class Mastermind:
    def __init__(self, site_id="STOW", type_id='Standard Work Violation'):
        self.site_id = site_id
        self.type_id = type_id
        self.df = GrabDataframe.get_df_excel(GrabWidget().get_path())
        self.driver = GrabWeb.open_driver(GrabWidget.get_driver())
        self.driver.implicitly_wait(1)

    def mm_prepare(self):
        self.df.sort_values('process')
        self.df['error_date'] = self.df['error_date'].astype(str)
        GrabWeb.get_web_site(
            f'https://mastermind.dub.amazon.com/defect_engine/defects/new?area_id={site_dict[self.site_id]}')
        select = Select(self.driver.find_element('id', 'types_select'))
        select.select_by_value(str(type_dict[self.site_id][self.type_id]))
        WebDriverWait(self.driver, timeout=10).until(lambda d: d.find_element(By.ID, "form-button"))
        return select

    def mm_loop(self, submit, complete):
        for index, row in self.df.iterrows():
            check_cancel = GrabWidget().get_progress_bar(index + 1, len(self.df))

            if not check_cancel:
                logger.warning(f'Closed at: {index - 1}')
                break
            if self.site_id != row['process'].upper():
                self.site_id = row['process'].upper()
                self.driver.get(
                    f'https://mastermind.dub.amazon.com/defect_engine/defects/new?area_id={site_dict[self.site_id]}')
            submit(index, row)
            complete(index, row)

    def mm_fill_submit(self, index, row):
        selector = WebDriverWait(self.driver, timeout=10).until(lambda d: d.find_element(By.ID, "types_select"))
        select = Select(selector)
        select.select_by_value(str(type_dict[self.site_id][self.type_id]))
        btn = WebDriverWait(self.driver, timeout=10).until(lambda d: d.find_element(By.ID, "form-button"))
        GrabWeb().fill_text_area(row['defect_associate'], By.ID, 'user_id')
        GrabWeb().fill_text_area(row['error_date'], By.ID, 'defect_date')
        GrabWeb().fill_text_area(row['container_id'], By.ID, 'defect_container')
        if self.site_id == "STOW" or self.site_id == "RECEIVE" or self.site_id == "ICQA":
            GrabWeb().fill_text_area(row['po'], By.ID, 'defect_po')
        GrabWeb().fill_text_area(row['problem_asin'], By.ID, 'defect_asin')
        GrabWeb().fill_text_area(row['incorrect_quantity'], By.ID, 'defect_qty')
        GrabWeb().fill_text_area(row['violation_details'], By.ID, 'defect_comment')
        time.sleep(0.5)
        btn.click()
        time.sleep(0.5)
        logger.info(f"Button click: {str(index+1)}")

    def mm_completion(self, index, row):
        if self.driver.find_elements('class name', 'past-defect'):
            msg = self.driver.find_element('class name', 'past-defect').text
            self.df.loc[index, 'Completion'] = msg
            logger.info(f"Registered {row['defect_associate']} with index:{str(index)} as {msg}")
        elif self.driver.find_elements('class name', 'defect-validation-error'):
            msg = self.driver.find_element('class name', 'defect-validation-error').text
            self.df.loc[index, 'Completion'] = msg
            logger.warning(f"Registered {row['defect_associate']} with index:{str(index)} as {msg}")
        else:
            self.df.loc[index, 'Completion'] = 'ERROR'
            logger.critical(f"Registered {row['defect_associate']} with index:{str(index)} as unknown error")

    def mm_end(self):
        self.df.to_excel('feedback_entries.xlsx', sheet_name='result', index=False)
        logger.info('Saved feedback_entries.xlsx within script folder')
        self.driver.close()
        logger.info('Driver closed')
