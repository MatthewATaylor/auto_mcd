from ItemSetting import ItemSetting

from selenium.webdriver.common.by import By


class RadioItemSetting(ItemSetting):
    def __init__(self, radio_buttons, scroll_container):
        self.radio_buttons = radio_buttons
        super().__init__(scroll_container, self.__get_cost())

    def __get_cost(self):
        """Returns a list of the cost of each respective radio button selection"""
        costs = [0.0 for button in self.radio_buttons]
        for i, button in enumerate(self.radio_buttons):
            potential_cost_divs = button.find_elements(By.XPATH, ".//div[not(*)]")
            for div in potential_cost_divs:
                if "$" in div.text:
                    cost_str = ""
                    for char in div.text:
                        if char.isdecimal() or char == "." or char == "-":
                            cost_str += char
                    costs[i] = float(cost_str)
                    break
        return costs

    def set_value(self, value):
        """Where value is an index of the radio_buttons list"""
        self.scroll_to_element(self.radio_buttons[value])
        self.radio_buttons[value].click()
