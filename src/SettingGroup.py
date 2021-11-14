from DriverUtils import DriverUtils
from NumericItemSetting import NumericItemSetting
from CheckboxItemSetting import CheckboxItemSetting
from constants import *

from selenium.webdriver.common.by import By


class SettingGroup:
    def __init__(self, expansion_button):
        self.expansion_button = expansion_button
        self.is_opened = expansion_button.get_attribute("aria-expanded") == "true"

    def open(self):
        DriverUtils.scroll_to_element(self.expansion_button)
        DriverUtils.scroll_amount(-ITEM_DIALOG_BANNER_HEIGHT)
        if not self.is_opened:
            self.expansion_button.click()
            self.is_opened = True

    def close(self):
        DriverUtils.scroll_to_element(self.expansion_button)
        DriverUtils.scroll_amount(-ITEM_DIALOG_BANNER_HEIGHT)
        if self.is_opened:
            self.expansion_button.click()
            self.is_opened = False

    def get_settings(self, driver):
        """This should only be run once all groups have been closed"""
        self.open()

        checkbox_settings = [
            CheckboxItemSetting(element) for element in driver.find_elements(
                By.XPATH, "//div[@role='dialog']//input[@type='checkbox']"
            )
        ]
        numerical_settings = []

        increment_buttons = driver.find_elements(By.XPATH, "//div[@role='dialog']//button[@aria-label='Increment']")
        for increment_button in increment_buttons:
            decrement_button = None
            default_value = 0
            label_divs = increment_button.find_elements(By.XPATH, "./preceding-sibling::div")
            if len(label_divs) > 0:
                default_value = int(label_divs[0].text)
                decrement_button = label_divs[0].find_elements(
                    By.XPATH, "./preceding-sibling::button[@aria-label='Decrement']"
                )
            numerical_settings.append(NumericItemSetting(default_value, increment_button, decrement_button))

        self.close()

        settings = []
        settings += checkbox_settings
        settings += numerical_settings
        return settings
