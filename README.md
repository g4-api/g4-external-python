# Plugin Repository - Quick Start Guide

## Steps to Implement a New Plugin

To add a new plugin, you need to create **two** files:

1. A **Plugin Class** under the `plugins/` package (you can organize by creating sub-packages if needed).
2. A **Manifest** file under the `manifests/` folder (sub-packages are also supported here).

### 1. Create a Plugin Class

Create a Python class that inherits from `PluginBase` and place it in the `plugins/` package. Here’s an example of how to implement a plugin, including how to retrieve and use the WebDriver for UI automation:

```python
from models.plugin_response_model import PluginResponseModel
from plugins.plugin_base import PluginBase
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class InvokePythonClick(PluginBase):
    def __init__(self, setup_model):
        """
        Initializes the plugin with the setup model, which contains the WebDriver for UI automation.

        Args:
            setup_model (SetupModel): Contains necessary configurations such as the WebDriver.
        """
        super().__init__(setup_model)

    def invoke(self, action_request):
        """
        Executes the plugin's logic, such as performing a click action on a UI element.

        Args:
            action_request (dict): The action request containing the entity and the rules for locating and clicking the element.

        Returns:
            PluginResponseModel: The response model after execution.
        """
        # Extract the element details from the action_request
        rule = action_request["entity"]
        locator_type = By.CSS_SELECTOR if rule["locator"] == "CssSelector" else By.XPATH
        locator_value = rule["onElement"]

        # Access the WebDriver from the plugin setup model
        driver = self.plugin_setup_model.driver

        # Wait for the element to be present and perform a click action
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((locator_type, locator_value))
        )
        element.click()

        # Return a PluginResponseModel after the action is performed
        return PluginResponseModel()
```

### Important Details:
- The WebDriver instance for UI automation is accessed through `self.plugin_setup_model.driver`.
- You can use this WebDriver to perform Selenium-based actions such as locating elements, clicking, and interacting with web elements in the browser.

### 2. Create a Manifest File

Create a JSON manifest file under the `manifests/` folder. The `key` in the manifest must match the plugin class name, and at least one example must be included.

**Example Manifest:**

```json
{
    "key": "InvokePythonClick",
    "aliases": ["PythonClick", "LeftPythonClick"],
    "author": {
        "name": "Your Name",
        "link": "https://www.example.com"
    },
    "categories": ["UI", "Browser"],
    "description": [
        "### Purpose",
        "This plugin performs click actions on specified web elements.",
        "",
        "### Features",
        "- Supports multiple locator strategies.",
        "- Can handle conditional clicks based on element state."
    ],
    "summary": [
        "The `InvokePythonClick` plugin is designed to perform click actions on web elements.",
        "It can be used in automation testing, RPA workflows, or any browser interaction tasks."
    ],
    "pluginType": "Action",
    "manifestVersion": 4,
    "examples": [
        {
            "description": [
                "Perform a click action on an element with the ID `submitButton` using a CSS selector."
            ],
            "rule": {
                "locator": "CssSelector",
                "onElement": "#submitButton",
                "pluginName": "InvokePythonClick"
            }
        }
    ]
}
```

### 3. G4 Engine Settings

To use this repository with the G4 engine, add the following settings to the G4 automation request:

```json
"settings": {
    "pluginsSettings": {
        "externalRepositories": [
            {
                "name": "MainAPIService",
                "url": "http://localhost:9999",
                "version": 4
            }
        ]
    }
}
```

## Key Notes

- **Plugin Class**: The plugin class must inherit from `PluginBase`.
- **Manifest Key**: The `key` in the manifest must match the plugin class name.
- **Manifest Example**: The manifest must contain at least one example for it to be valid.
- **Markdown Support**: The `description` and `summary` fields in the manifest support markdown syntax. Each array element represents a new line.
- **WebDriver Access**: The WebDriver instance for UI automation is accessed through `self.plugin_setup_model.driver`.