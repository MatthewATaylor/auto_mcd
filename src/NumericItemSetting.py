from DriverUtils import DriverUtils
from ItemSetting import ItemSetting
from constants import *

from selenium.webdriver.common.by import By


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