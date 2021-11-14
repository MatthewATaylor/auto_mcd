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
        super().__init__(0)  # Can't determine if actually checked or not, will assume free cost
        self.element = element
        self.scroll_container = scroll_container

    def click(self):
        DriverUtils.scroll_to_element(self.element)
        DriverUtils.scroll_element_amount(self.scroll_container, -ITEM_DIALOG_BANNER_HEIGHT)
        self.element.click()

    def set_value(self, value):
        """Change value of checkbox if value is 1, otherwise keep default"""
        if value:
            self.click()
