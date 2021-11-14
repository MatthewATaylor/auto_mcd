from DriverUtils import DriverUtils
from ItemSetting import ItemSetting
from constants import *


class CheckboxItemSetting(ItemSetting):
    def __init__(self, element, scroll_container):
        # Probably don't even need name
        # potential_name_divs = element.find_element(By.XPATH, "./following-sibling::label//div[not(*)]")
        # for div in potential_name_divs:
        #     if len(div.text) != 0:
        #         self.name = div.text
        self.element = element
        super().__init__(scroll_container, 0)  # Can't determine if actually checked or not, will assume free cost
        # TODO actually get checkbox cost

    def click(self):
        self.scroll_to_element(self.element)
        self.element.click()

    def set_value(self, value):
        """Change value of checkbox if value is 1, otherwise keep default"""
        if value:
            self.click()
