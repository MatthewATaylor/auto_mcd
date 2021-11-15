"""All of the below functions require that a menu item was clicked beforehand"""


from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException

from SettingGroup import SettingGroup
from DriverUtils import DriverUtils
from constants import *


def current_item_is_available(driver):
    return len(driver.find_elements(By.XPATH, "//button/div[text()='Unavailable']")) == 0


def exit_current_item(driver):
    close_button = driver.find_element(By.XPATH, "//div[@role='dialog']//button[@aria-label='Close']")
    DriverUtils.scroll_to_element(close_button)
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


def set_current_item_quantity(driver, quantity):
    """
    quantity should be greater than or equal to 1
    Note: This is unreliable and that d attribute will probably change in the near future.
        May want to not use this in our final version
    """

    increment_d = "M19.333 11H13V4.665h-2v6.333H4.667v2H11v6.334h2v-6.334h6.333z"
    increment_button = driver.find_elements(
        By.XPATH,
        f"//div[@role='dialog']//button//*[local-name()='svg']//*[local-name()='path' and @d='{increment_d}']/../.."
    )
    if len(increment_button) == 0:
        print("NOTE: Unable to increase item quantity, leaving as 1")
        return

    scroll_container = driver.find_element(By.XPATH, "//div[@data-focus-lock-disabled]/div")
    DriverUtils.scroll_to_element(increment_button[0])
    DriverUtils.scroll_element_amount(scroll_container, -ITEM_DIALOG_BANNER_HEIGHT)

    current_quantity = 1
    while quantity - current_quantity > 0:
        increment_button[0].click()
        current_quantity += 1


def add_current_item_to_cart(driver):
    while True:
        potential_add_buttons = driver.find_elements(By.XPATH, "//div[@role='dialog']//button")
        for button in potential_add_buttons:
            sub_divs = button.find_elements(By.XPATH, ".//div[not(*)]")
            for div in sub_divs:
                if "Add" in div.text:
                    scroll_container = driver.find_element(By.XPATH, "//div[@data-focus-lock-disabled]/div")
                    DriverUtils.scroll_to_element(button)
                    DriverUtils.scroll_element_amount(scroll_container, -ITEM_DIALOG_BANNER_HEIGHT)
                    button.click()
                    while True:
                        try:
                            driver.find_element(By.XPATH, "//div[@role='dialog']//button[@aria-label='Close']")
                        except NoSuchElementException:
                            return
    # print("NOTE: Unable to add item to cart, exiting")
    # exit_current_item(driver)
