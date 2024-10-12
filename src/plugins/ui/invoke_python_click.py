from selenium.webdriver.common.by import By
from selenium.webdriver.support import wait, expected_conditions

from models.plugin_response_model import PluginResponseModel
from models.setup_model import SetupModel
from plugins.plugin_base import PluginBase


class InvokePythonClick(PluginBase):
    """
    A plugin to handle clicking elements on a web page using Selenium WebDriver.

    This plugin locates an element on the web page using the provided action request, waits for the
    element to be present, and clicks it. It extends the base plugin class `PluginBase`.

    Args:
        plugin_setup_model (SetupModel): The setup model which contains necessary configurations like the
        WebDriver instance.

    Methods:
        invoke(action_request): Executes the action of finding the element and clicking it, then returns
        a PluginResponseModel.
    """

    def __init__(self, plugin_setup_model: SetupModel):
        """
        Initializes the InvokePythonClick plugin with the provided setup model.

        Args:
            plugin_setup_model (SetupModel): The setup model, including configurations such as WebDriver.
        """
        super().__init__(plugin_setup_model)

    def invoke(self, action_request) -> PluginResponseModel:
        """
        Executes the click action based on the provided action request.

        Args:
            action_request (dict): The action request containing the entity and the rules for locating and clicking
            the element.

        Returns:
            PluginResponseModel: A response model after the click action has been performed.
        """
        # Extract the rule (contains information about the element to be clicked)
        rule = action_request["entity"]

        # Determine the locator type (default to XPath if locator_type is not specified in the rule)
        locator_type = By.XPATH if not rule["locator"] else {rule["locator"]}

        # Create a locator tuple based on the locator type and the element's identifier (onElement)
        locator = (locator_type, rule["onElement"])

        # Initialize a WebDriverWait instance to wait for the element to be present on the page (max wait: 10 seconds)
        driver_wait = wait.WebDriverWait(self.plugin_setup_model.driver, 10)

        # Wait until the element is located and present on the DOM
        element = driver_wait.until(expected_conditions.presence_of_element_located(locator))

        # Click the located element
        element.click()

        # Return an empty PluginResponseModel after the click action
        return PluginResponseModel()
