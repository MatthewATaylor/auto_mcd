import random
import datetime
from typing import List
import time

from PIL import Image
import requests
from io import BytesIO
import selenium.common.exceptions
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import numpy as np


MAIN_BANNER_HEIGHT = 134
ITEM_DIALOG_BANNER_HEIGHT = 64


class DriverUtils:
    driver = None

    @classmethod
    def set_driver(cls, new_driver):
        cls.driver = new_driver

    @classmethod
    def scroll_to_element(cls, element):
        try:
            cls.driver.execute_script("arguments[0].scrollIntoView();", element)
        except selenium.common.exceptions.JavascriptException:
            print("NOTE: Unable to scroll to element")
        print("Scrolling to element...")
        time.sleep(2)

    @classmethod
    def scroll_amount(cls, amount):
        cls.driver.execute_script(f"window.scrollBy(0, {amount});")
        print("Scrolling up...")
        time.sleep(2)


class ItemSetting:
    def __init__(self, cost):
        self.cost = cost

    def set_value(self, value):
        pass


class NumericItemSetting(ItemSetting):
    def __init__(self, default_value, increment_element, decrement_element):
        self.default_value = default_value
        self.increment_element = increment_element
        self.decrement_element = decrement_element  # May be None (when default_value is 0)
        super().__init__(self.get_cost())

    def get_cost(self):
        parent_element = self.increment_element.find_element(By.XPATH, "./../../div")
        potential_cost_divs = parent_element.find_elements(By.XPATH, ".//div[not(*)]")
        for div in potential_cost_divs:
            if "$" in div.text:
                return float(div.text[1:])
        return 0

    def set_value(self, value):
        """Where value is probably either 0 or 1"""
        DriverUtils.scroll_to_element(self.increment_element)
        DriverUtils.scroll_amount(-ITEM_DIALOG_BANNER_HEIGHT)
        delta_value = value - self.default_value
        while delta_value > 0:
            self.decrement_element.click()
            delta_value += 1
        while delta_value < 0:
            self.increment_element.click()
            delta_value -= 1


class CheckboxItemSetting(ItemSetting):
    def __init__(self, element):
        # Probably don't even need name
        # potential_name_divs = element.find_element(By.XPATH, "./following-sibling::label//div[not(*)]")
        # for div in potential_name_divs:
        #     if len(div.text) != 0:
        #         self.name = div.text
        super().__init__(0)  # Can't determine if actually checked or not, will assume free cost
        self.element = element

    def click(self):
        DriverUtils.scroll_to_element(self.element)
        DriverUtils.scroll_amount(-ITEM_DIALOG_BANNER_HEIGHT)
        self.element.click()

    def set_value(self, value):
        """Change value of checkbox if value is 1, otherwise keep default"""
        if value:
            self.click()


class SettingGroup:
    def __init__(self, expansion_button):
        self.expansion_button = expansion_button
        self.is_opened = expansion_button.get_attribute("aria-expanded") == "true"
        self.settings: List[ItemSetting] = []

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

        self.settings += checkbox_settings
        self.settings += numerical_settings

        self.close()


def str_is_num(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def str_is_dollar_amt(s):
    return len(s) > 1 and s[0] == "$" and str_is_num(s[1:])


def str_is_cal_count(s):
    return " Cal." in s


def str_is_limit(s):
    return "Limit of " in s and s.removeprefix("Limit of ").isnumeric()


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
    close_buttons = driver.find_elements(By.XPATH, "//div[@role='dialog']//button[@aria-label='Close']")
    if len(close_buttons) == 1:
        close_buttons[0].click()


def scan_item_info(menu_item, all_item_info):
    """Get info about the item from the all_item_info divs, and add it to the menu_item dict"""
    try:
        for item_info in all_item_info:  # Look through each div without a child element
            item_info_str = item_info.text
            if len(item_info_str) > 0 and not str_is_cal_count(item_info_str):
                if str_is_dollar_amt(item_info_str):
                    menu_item["price"] = float(item_info_str[1:])
                elif str_is_limit(item_info_str):
                    menu_item["limit"] = int(item_info_str.removeprefix("Limit of "))
                else:
                    menu_item["name"] = item_info_str
    except selenium.common.exceptions.StaleElementReferenceException:
        # Scrolling makes some divs become stale
        print("NOTE: Stale element reference")


def finalize_menu_item(menu_item, category_item_list):
    """Add final info to the menu_item dict, where category_item_list is the root item element"""
    if "limit" not in menu_item:
        menu_item["limit"] = 0
    item_imgs = category_item_list.find_elements(By.XPATH, ".//picture/img")
    if len(item_imgs) > 0:
        menu_item["img"] = item_imgs[0].get_attribute("src")
    else:
        menu_item["img"] = ""
    menu_item["element"] = category_item_list


def get_menu_items_from_category(driver, category):
    """Generate the category_items list, a list of dicts representing all items of the given category"""
    category_items = []
    list_elements = driver.find_elements(By.XPATH, "//li")
    for list_element in list_elements:
        category_headings = list_element.find_elements(By.XPATH, f".//h2[text()='{category}']")
        if len(category_headings) > 0:
            category_item_lists = list_element.find_elements(By.XPATH, "./ul/li")
            for category_item_list in category_item_lists:
                menu_item = dict()
                DriverUtils.scroll_to_element(category_item_list)  # Scroll to load image
                all_item_info = category_item_list.find_elements(By.XPATH, ".//div[not(*)]")
                scan_item_info(menu_item, all_item_info)
                if menu_item:  # Info was added by scan_item_info
                    finalize_menu_item(menu_item, category_item_list)
                    category_items.append(menu_item)
    return category_items


def get_menu_items(driver, menu_categories):
    menu_items = []
    for cat in menu_categories:
        menu_items += get_menu_items_from_category(driver, cat)
    return menu_items


def item_available_after_midnight(url):
    if url == "":
        return True
    response = requests.get(url)
    image = Image.open(BytesIO(response.content))
    image = np.array(image)
    avg_banner_color = np.array([244, 211, 130])
    average_color = np.mean(np.mean(image[:9, :, :], axis=0), axis=0)
    return not np.all(np.abs(average_color - avg_banner_color) <= 1e1)


def time_is_past_midnight():
    """In other words, time is between midnight and 4:30 am (end of dinner)"""
    current_time = datetime.datetime.now().time()
    midnight = datetime.time(0, 0, 0)
    dinner_end_time = datetime.time(4, 30, 0)
    return midnight < current_time < dinner_end_time


def get_menu_categories(driver):
    # Hmm "ex" may be a randomized class name
    list_elements = driver.find_elements(By.CLASS_NAME, 'ex')
    return [elm.text for elm in list_elements]


def click_item(item):
    DriverUtils.scroll_to_element(item["element"])
    DriverUtils.scroll_amount(-MAIN_BANNER_HEIGHT)  # Uncover item from top navigation banner
    item["element"].click()


def current_item_is_available(driver):
    """Note: must click item before performing this check"""
    return len(driver.find_elements(By.XPATH, "//button/div[text()='Unavailable']")) == 0


def exit_current_item(driver):
    close_button = driver.find_element(By.XPATH, "//div[@role='dialog']//button[@aria-label='Close']")
    DriverUtils.scroll_to_element(close_button)
    close_button.click()


def get_current_setting_groups(driver):
    group_expander_buttons = driver.find_elements(By.XPATH, "//div[@role='dialog']//button[@aria-expanded]")
    setting_groups = [SettingGroup(button) for button in group_expander_buttons]
    for setting_group in setting_groups:
        setting_group.close()
    for setting_group in setting_groups:
        setting_group.get_settings(driver)
    return setting_groups


def main():
    past_midnight = time_is_past_midnight()

    driver = webdriver.Firefox()
    DriverUtils.set_driver(driver)
    driver.get("https://www.ubereats.com/store/mcdonalds-463-mass-ave-cambridge/PiyOQ48sRteUFdtRnOvIBw")

    validate_address(driver)
    exit_second_dialog(driver)

    menu_categories = [
        #"Sweets & Treats",
        #"Condiments",
        #"Fries, Sides & More",
        #"McCafé",
        #"McCafé Bakery",
        #"Beverages",
        "Individual Items",  # Just look at individual items for testing (most complicated)
        #"Homestyle Breakfasts",
        #"Snacks, Sides & More"
    ]

    menu_items = get_menu_items(driver, menu_categories)
    for item in menu_items:
        print(item)
    random.shuffle(menu_items)

    for i in range(5):
        print()

        rand_item = menu_items[i]
        print(rand_item["name"])

        available_after_midnight = item_available_after_midnight(rand_item["img"])
        print(f"Item is available after midnight: {available_after_midnight}")
        if not available_after_midnight and past_midnight:
            print("Time is after after midnight, skipping item")
            continue

        # For each item selected by randomizer
        DriverUtils.scroll_to_element(rand_item["element"])
        click_item(rand_item)
        if not current_item_is_available(driver):
            print("Item is unavailable")
            exit_current_item(driver)
            continue

        setting_groups = get_current_setting_groups(driver)
        for group in setting_groups:
            print(f"    Opened: {group.is_opened}")
            print("    Settings:")
            for setting in group.settings:
                if isinstance(setting, NumericItemSetting):
                    print(f"        Numeric    {setting.cost}")
                elif isinstance(setting, CheckboxItemSetting):
                    print("        Checkbox")
                else:
                    print("        ????")

        exit_current_item(driver)


if __name__ == '__main__':
    main()


# PAGE LAYOUT AND THINGS TO CONSIDER

# "Comes With"
    # -/+ buttons that may have value already selected (and may be at max value)
    # Checkboxes that may already be checked
# "Additions" (sometimes)
    # -/+ buttons
# "Special Instructions"
    # Checkboxes (Plain, Substitute Mac Sauce)
# Add button may say "Unavailable instead"
    # Will have to be dynamically compensated for when attempting purchase
# Arrow buttons that open up additional options (like those above)
# McNuggets (different style configurations)
    # Select sauce menu (-/+ buttons, max two/three sauce packages)
# Large, medium, small options for most drinks

# PROCEDURE

# Get user info from GUI
# Scan page to get list of items and prices
# Have randomizer process item list and select items
#   For each item selected
#       Scrape item options if not done so already
#       Randomly select options
# Pay for food (perhaps with verification that the cost is ok)
