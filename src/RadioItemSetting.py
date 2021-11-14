from ItemSetting import ItemSetting


class RadioItemSetting(ItemSetting):
    def __init__(self, radio_buttons, scroll_container):
        self.radio_buttons = radio_buttons
        super().__init__(scroll_container, self.__get_cost())

    def __get_cost(self):
        """Returns a list of the cost of each respective radio button selection"""
        return [0 for _ in self.radio_buttons]

    def set_value(self, value):
        """Where value is an index of the radio_buttons list"""
        self.scroll_to_element(self.radio_buttons[value])
        self.radio_buttons[value].click()
