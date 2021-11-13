import random

from PIL import Image
import requests
from io import BytesIO
import selenium.common.exceptions
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import numpy as np


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


def scroll_to_element(driver, element):
    try:
        driver.execute_script("arguments[0].scrollIntoView();", element)
    except selenium.common.exceptions.JavascriptException:
        print("NOTE: Unable to scroll to element")


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
                scroll_to_element(driver, category_item_list)  # Scroll to load image
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
    response = requests.get(url)
    image = Image.open(BytesIO(response.content))
    image = np.array(image)
    avg_banner_color = np.array([244, 211, 130])
    average_color = np.mean(np.mean(image[:9, :, :], axis=0), axis=0)
    return not np.all(np.abs(average_color - avg_banner_color) <= 1e1)


def get_menu_categories(driver):
    # Hmm "ex" may be a randomized class name
    list_elements = driver.find_elements(By.CLASS_NAME, 'ex')
    return [elm.text for elm in list_elements]


def main():
    driver = webdriver.Firefox()
    driver.get("https://www.ubereats.com/store/mcdonalds-463-mass-ave-cambridge/PiyOQ48sRteUFdtRnOvIBw")

    validate_address(driver)
    exit_second_dialog(driver)

    menu_categories = [
        "Sweets & Treats",
        "Condiments",
        "Fries, Sides & More",
        "McCafé",
        "McCafé Bakery",
        "Beverages",
        "Individual Items",
        "Homestyle Breakfasts",
        "Snacks, Sides & More"
    ]

    menu_items = get_menu_items(driver, menu_categories)
    for item in menu_items:
        print(item)
    random.shuffle(menu_items)

    rand_item = menu_items[0]
    print(rand_item["name"])
    print(item_available_after_midnight(rand_item["img"]))
    scroll_to_element(driver, rand_item["element"])
    driver.execute_script("window.scrollBy(0, -134);")  # Uncover item from top navigation banner
    rand_item["element"].click()


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
