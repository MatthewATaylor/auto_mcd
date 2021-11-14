from ItemSetting import ItemSetting

from selenium.webdriver.common.by import By


class CheckboxItemSetting(ItemSetting):
    def __init__(self, element, scroll_container):
        self.element = element
        super().__init__(scroll_container, self.__get_cost())

    def __get_cost(self):
        """We'll assume that a CHANGE in value costs money since we can't know the true checkbox state"""
        potential_cost_divs = self.element.find_elements(By.XPATH, ".//div[not(*)]")
        for div in potential_cost_divs:
            if "$" in div.text:
                cost_str = ""
                for char in div.text:
                    if char.isdecimal() or char == "." or char == "-":
                        cost_str += char
                return float(cost_str)
        return 0

    def click(self):
        self.scroll_to_element(self.element)
        self.element.click()

    def set_value(self, value):
        """Change value of checkbox if value is 1, otherwise keep default"""
        if value:
            self.click()
