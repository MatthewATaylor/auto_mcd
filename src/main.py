import random
import datetime
from typing import List

import selenium.common.exceptions
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from DriverUtils import DriverUtils
from MenuItem import MenuItem
from NumericItemSetting import NumericItemSetting
from CheckboxItemSetting import CheckboxItemSetting
from SettingGroup import SettingGroup


def validate_address(driver):
    """Fill out the initial address validation popup"""
    address_input = driver.find_element(By.ID, "location-typeahead-location-manager-input")
    address_input.send_keys("3 Ames st. Cambridge MA")
    while True:
        try:
            address_input = driver.find_element(By.ID, "location-typeahead-location-manager-input")
            address_input.send_keys(Keys.ENTER)
        except (selenium.common.exceptions.NoSuchElementException,
                selenium.common.exceptions.StaleElementReferenceException):
            break


def exit_second_dialog(driver):
    """If McDonald's is closed, another dialog pops up. Close out of it for testing"""
    # TODO in final version: halt purchase if this dialog pups up
    close_buttons = driver.find_elements(By.XPATH, "//div[@role='dialog']//button[@aria-label='Close']")
    if len(close_buttons) == 1:
        close_buttons[0].click()


def get_menu_items_from_category(driver, category):
    """Generate the category_items list, a list of dicts representing all items of the given category"""
    category_items = []
    list_elements = driver.find_elements(By.XPATH, "//li")
    for list_element in list_elements:
        category_headings = list_element.find_elements(By.XPATH, f".//h2[text()='{category}']")
        if len(category_headings) > 0:
            category_item_lists = list_element.find_elements(By.XPATH, "./ul/li")
            for category_item_list in category_item_lists:
                DriverUtils.scroll_to_element(category_item_list)  # Scroll to load image
                all_item_info = category_item_list.find_elements(By.XPATH, ".//div[not(*)]")
                try:
                    menu_item = MenuItem(all_item_info, category_item_list, category)
                    category_items.append(menu_item)
                except ValueError:
                    print("NOTE: Skipping incomplete menu item construction")
    return category_items


def get_menu_items(driver, menu_categories):
    menu_items = []
    for cat in menu_categories:
        menu_items += get_menu_items_from_category(driver, cat)
    return menu_items


def time_is_past_midnight():
    """In other words, time is between midnight and 4:30 am (end of dinner)"""
    current_time = datetime.datetime.now().time()
    midnight = datetime.time(0, 0, 0)
    dinner_end_time = datetime.time(4, 30, 0)
    return midnight < current_time < dinner_end_time


def current_item_is_available(driver):
    """Note: must click item before performing this check"""
    return len(driver.find_elements(By.XPATH, "//button/div[text()='Unavailable']")) == 0


def exit_current_item(driver):
    close_button = driver.find_element(By.XPATH, "//div[@role='dialog']//button[@aria-label='Close']")
    DriverUtils.scroll_to_element(close_button)
    close_button.click()


def get_current_item_settings(driver):
    """Note: must click item before getting settings"""
    group_expander_buttons = driver.find_elements(By.XPATH, "//div[@role='dialog']//button[@aria-expanded]")
    setting_groups = [SettingGroup(button) for button in group_expander_buttons]
    settings = []
    for setting_group in setting_groups:
        setting_group.close()  # Close all groups to only focus on one at a time
    for setting_group in setting_groups:
        settings += setting_group.get_settings(driver)
    return settings


def main():
    past_midnight = time_is_past_midnight()

    driver = webdriver.Firefox()
    DriverUtils.set_driver(driver)
    driver.get("https://www.ubereats.com/store/mcdonalds-463-mass-ave-cambridge/PiyOQ48sRteUFdtRnOvIBw")

    validate_address(driver)
    exit_second_dialog(driver)

    menu_categories = [
        # "Sweets & Treats",
        # "Condiments",
        # "Fries, Sides & More",
        # "McCafé",
        # "McCafé Bakery",
        # "Beverages",
        "Individual Items",  # Just look at individual items for testing (most complicated)
        # "Homestyle Breakfasts",
        # "Snacks, Sides & More"
    ]

    menu_items: List[MenuItem] = get_menu_items(driver, menu_categories)
    for item in menu_items:
        print(f"{item.name}    ${item.price}    Limit: {item.limit}    Img: {item.img_url}")
    random.shuffle(menu_items)

    for i in range(5):
        print()

        rand_item = menu_items[i]
        print(rand_item.name)

        available_after_midnight = rand_item.is_available_after_midnight()
        print(f"Item is available after midnight: {available_after_midnight}")
        if not available_after_midnight and past_midnight:
            print("Time is after after midnight, skipping item")
            continue

        # For each item selected by randomizer
        rand_item.click()
        if not current_item_is_available(driver):
            print("Item is unavailable")
            exit_current_item(driver)
            continue

        print("Settings:")
        settings = get_current_item_settings(driver)
        for setting in settings:
            if isinstance(setting, NumericItemSetting):
                print(f"        Numeric    {setting.cost}")
            elif isinstance(setting, CheckboxItemSetting):
                print("        Checkbox")
            else:
                print("        what the fuck")

        exit_current_item(driver)


if __name__ == '__main__':
    main()


# TODO Large, medium, small options for most drinks


# PROCEDURE

# Get user info from GUI
# Scan page to get list of items and prices
# Have randomizer process item list and select items
#   For each item selected
#       Scrape item options if not done so already
#       Randomly select options
# Pay for food (perhaps with verification that the cost is ok)
