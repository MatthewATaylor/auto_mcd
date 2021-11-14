from DriverUtils import DriverUtils
from constants import *


class ItemSetting:
    def __init__(self, scroll_container, cost):
        self.scroll_container = scroll_container
        self.cost = cost

    def set_value(self, value):
        pass

    def scroll_to_element(self, element):
        DriverUtils.scroll_to_element(element)
        DriverUtils.scroll_element_amount(self.scroll_container, -ITEM_DIALOG_BANNER_HEIGHT)
