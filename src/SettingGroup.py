from DriverUtils import DriverUtils
from NumericItemSetting import NumericItemSetting
from CheckboxItemSetting import CheckboxItemSetting
from RadioItemSetting import RadioItemSetting
from constants import *

from selenium.webdriver.common.by import By


class SettingGroup:
    def __init__(self, expansion_button, scroll_container):
        self.expansion_button = expansion_button
        self.scroll_container = scroll_container
        self.is_opened = expansion_button.get_attribute("aria-expanded") == "true"

    def open(self):
        if not self.is_opened:
            DriverUtils.scroll_to_element(self.expansion_button)
            DriverUtils.scroll_element_amount(self.scroll_container, -ITEM_DIALOG_BANNER_HEIGHT)
            self.expansion_button.click()
            self.is_opened = True

    def close(self):
        if self.is_opened:
            DriverUtils.scroll_to_element(self.expansion_button)
            DriverUtils.scroll_element_amount(self.scroll_container, -ITEM_DIALOG_BANNER_HEIGHT)
            self.expansion_button.click()
            self.is_opened = False

    def set_settings(self, driver):
        """This should only be run once all groups have been closed"""
        self.open()

        checkbox_settings = self.get_checkbox_settings(driver)
        for checkbox_setting in checkbox_settings:
            print(f"    Checkbox - ${checkbox_setting.cost}")
            checkbox_setting.set_value(1)

        numeric_settings = self.get_numeric_settings(driver)
        for numeric_setting in numeric_settings:
            print(f"    Numeric - ${numeric_setting.cost} - Default: {numeric_setting.default_value}")
            numeric_setting.set_value(0)

        radio_settings = self.get_radio_settings(driver)
        for radio_setting in radio_settings:
            print(f"    Radio - ${radio_setting.cost}")
            radio_setting.set_value(1)

        self.close()

    def get_checkbox_settings(self, driver):
        checkboxes = driver.find_elements(By.XPATH, "//div[@role='dialog']//input[@type='checkbox']")
        checkbox_settings = []
        for checkbox in checkboxes:
            checkbox_name = checkbox.get_attribute("name")
            label = driver.find_element(By.XPATH, f"//div[@role='dialog']//label[@for='{checkbox_name}']")
            checkbox_settings.append(CheckboxItemSetting(label, self.scroll_container))
        return checkbox_settings

    def get_numeric_settings(self, driver):
        numeric_settings = []
        increment_buttons = driver.find_elements(By.XPATH, "//div[@role='dialog']//button[@aria-label='Increment']")
        for increment_button in increment_buttons:
            decrement_button = None
            default_value = 0
            label_divs = increment_button.find_elements(By.XPATH, "./preceding-sibling::div")
            if len(label_divs) > 0:
                default_value = int(label_divs[0].text)
                decrement_button = label_divs[0].find_element(
                    By.XPATH, "./preceding-sibling::button[@aria-label='Decrement']"
                )
            numeric_settings.append(
                NumericItemSetting(default_value, increment_button, decrement_button, self.scroll_container)
            )
        return numeric_settings

    def get_radio_settings(self, driver):
        radio_button_settings = []
        radio_buttons = driver.find_elements(By.XPATH, "//div[@role='dialog']//input[@type='radio']")
        while len(radio_buttons) > 0:
            current_setting_labels = []
            button_name = radio_buttons[0].get_attribute("name")
            for button in radio_buttons.copy():
                if button.get_attribute("name") == button_name:
                    button_id = button.get_attribute("id")
                    button_label = driver.find_element(
                        By.XPATH, f"//div[@role='dialog']//label[@for='{button_id}']"
                    )
                    current_setting_labels.append(button_label)
                    radio_buttons.remove(button)
            radio_button_settings.append(RadioItemSetting(current_setting_labels, self.scroll_container))
        return radio_button_settings
