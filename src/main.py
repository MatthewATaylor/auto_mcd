import random
import datetime
from typing import List
import tkinter as tk

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from MenuItem import MenuItem
from current_item_processing import *


def validate_address(driver):
    """Fill out the initial address validation popup"""
    address_input = driver.find_element(By.ID, "location-typeahead-location-manager-input")
    address_input.send_keys("3 Ames st. Cambridge MA")
    while True:
        try:
            address_input = driver.find_element(By.ID, "location-typeahead-location-manager-input")
            address_input.send_keys(Keys.ENTER)
        except (NoSuchElementException, StaleElementReferenceException):
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


def run_scraper():
    past_midnight = time_is_past_midnight()

    driver = webdriver.Firefox()
    DriverUtils.set_driver(driver)
    driver.get("https://www.ubereats.com/store/mcdonalds-463-mass-ave-cambridge/PiyOQ48sRteUFdtRnOvIBw")

    validate_address(driver)
    exit_second_dialog(driver)

    # TODO get McCafé to work
    menu_categories = [
        "Sweets & Treats",
        "Condiments",
        "Fries, Sides & More",
        # "McCafé",
        "McCafé Bakery",
        "Beverages",
        "Individual Items",
        "Homestyle Breakfasts",
        "Snacks, Sides & More"
    ]

    menu_items: List[MenuItem] = get_menu_items(driver, menu_categories)
    for item in menu_items.copy():
        # TODO get shakes to work
        if "Shake" in item.name:
            menu_items.remove(item)
        else:
            print(f"{item.name}    ${item.price}    Limit: {item.limit}    Img: {item.img_url}")
    random.shuffle(menu_items)

    # TODO integration with randomizer
    # Set up randomizer's menu using menu_items list
    # Have randomizer click on items to purchase and then run set_current_item_settings
    # set_current_item_settings calls set_settings for every SettingGroup in the item
    # Each SettingGroup's set_settings can have the randomizer call set_value for the different setting types
    # While doing this, subtract from total budget using ItemSetting and MenuItem cost values

    # Temp test
    for i in range(len(menu_items)):
        print()

        rand_item = menu_items[i]
        print(rand_item.name)

        available_after_midnight = rand_item.is_available_after_midnight()
        print(f"Item is available after midnight: {available_after_midnight}")
        if not available_after_midnight and past_midnight:
            print("Time is after after midnight, skipping item")
            continue

        rand_item.click()
        if not current_item_is_available(driver):
            print("Item is unavailable")
            exit_current_item(driver)
            continue

        print("Choosing settings...")
        set_current_item_settings(driver)

        exit_current_item(driver)


def main():
    # TODO make a real GUI

    window = tk.Tk()
    window.title = "auto_mcd"
    # window.attributes("-fullscreen", True)

    tk.Button(
        text="Enter",
        width=50,
        height=5,
        bg="black",
        fg="white",
        command=run_scraper
    ).pack()

    window.mainloop()


if __name__ == '__main__':
    main()
