from selenium.common.exceptions import JavascriptException


class DriverUtils:
    driver = None

    @classmethod
    def set_driver(cls, new_driver):
        cls.driver = new_driver

    @classmethod
    def scroll_to_element(cls, element):
        try:
            cls.driver.execute_script("arguments[0].scrollIntoView();", element)
        except JavascriptException:
            print("NOTE: Unable to scroll to element")

    @classmethod
    def scroll_amount(cls, amount):
        cls.driver.execute_script(f"window.scrollBy(0, {amount});")
