"""All of the below functions require that a menu item was clicked beforehand"""


from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException

from SettingGroup import SettingGroup
from DriverUtils import DriverUtils


def current_item_is_available(driver):
    return len(driver.find_elements(By.XPATH, "//button/div[text()='Unavailable']")) == 0


def exit_current_item(driver):
    close_button = driver.find_element(By.XPATH, "//div[@role='dialog']//button[@aria-label='Close']")
    DriverUtils.scroll_to_element(close_button)
    close_button.click()
    while True:
        try:
            close_button.click()
        except (NoSuchElementException, StaleElementReferenceException):
            break


def set_current_item_settings(driver):
    scroll_container = driver.find_element(By.XPATH, "//div[@data-focus-lock-disabled]/div")
    group_expansion_buttons = driver.find_elements(By.XPATH, "//div[@role='dialog']//button[@aria-expanded]")
    setting_groups = [SettingGroup(button, scroll_container) for button in group_expansion_buttons]
    for i, setting_group in enumerate(setting_groups):
        if i > 0:
            setting_group.close()  # Close all groups to only focus on one at a time
    for setting_group in setting_groups:
        setting_group.set_settings(driver)
