from io import BytesIO

import PIL.Image
import numpy as np
import requests
from PIL import Image
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By

from DriverUtils import DriverUtils
from str_checking import *
from constants import *


class MenuItem:
    def __init__(self, all_item_info, category_item_list, category):
        self.price = None
        self.limit = None
        self.name = None
        self.img_url = None
        self.element = None
        self.category = category

        self.perform_initial_scrape(all_item_info)
        if self.price is None:
            # Incorrect all_item_info
            raise ValueError

        self.finalize_setup(category_item_list)

    def perform_initial_scrape(self, all_item_info):
        try:
            for item_info in all_item_info:  # Look through each div without a child element
                item_info_str = item_info.text
                if len(item_info_str) > 0 and not str_is_cal_count(item_info_str):
                    if str_is_dollar_amt(item_info_str):
                        self.price = float(item_info_str[1:])
                    elif str_is_limit(item_info_str):
                        self.limit = int(item_info_str.removeprefix("Limit of "))
                    else:
                        self.name = item_info_str
        except StaleElementReferenceException:
            # Scrolling makes some divs become stale
            print("NOTE: Stale element reference")

    def finalize_setup(self, category_item_list):
        """Where category_list_item is the item's root element"""
        if self.limit is None:
            self.limit = 0
        item_imgs = category_item_list.find_elements(By.XPATH, ".//picture/img")
        if len(item_imgs) > 0:
            self.img_url = item_imgs[0].get_attribute("src")
        self.element = category_item_list

    def click(self):
        DriverUtils.scroll_to_element(self.element)
        DriverUtils.scroll_amount(-MAIN_BANNER_HEIGHT)  # Uncover item from top navigation banner
        self.element.click()

    def is_available_after_midnight(self):
        if self.img_url is None:
            return False
        response = requests.get(self.img_url)
        image = Image.open(BytesIO(response.content))
        image_np = np.array(image)
        image.close()
        avg_banner_color = np.array([244, 211, 130])
        average_color = np.mean(np.mean(image_np[:9, :, :], axis=0), axis=0)
        return not np.all(np.abs(average_color - avg_banner_color) <= 30)
