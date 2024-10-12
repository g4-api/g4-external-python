import json
import os
import re
import secrets
import string

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webdriver import WebDriver


def convert_to_camel_case(obj):
    """
    Recursively converts dictionary keys from snake_case to camelCase.

    Args:
        obj: The object to convert. Can be a dict, list, or other type.

    Returns:
        The converted object with all dictionary keys in camelCase.
    """

    def format_camel_case(snake_str: str) -> str:
        """
        Converts a snake_case string to camelCase.

        Args:
            snake_str (str): The snake_case string to convert.

        Returns:
            str: The converted camelCase string.
        """
        # Split the snake_case string into components.
        components = snake_str.split('_')
        # Combine the first component with the title-cased subsequent components.
        return components[0] + ''.join(x.title() for x in components[1:])

    # Check if the object is a list.
    if isinstance(obj, list):
        # Recursively convert each item in the list.
        return [convert_to_camel_case(o) for o in obj]
    # Check if the object is a dictionary.
    elif isinstance(obj, dict):
        # Create a new dictionary to store converted keys and values.
        new_dictionary = {}
        for key, value in obj.items():
            # Convert the key to camelCase.
            new_key = format_camel_case(key)
            # Recursively convert the value.
            new_dictionary[new_key] = convert_to_camel_case(value)
        return new_dictionary
    else:
        # Return the object as is if it's neither a list nor a dict.
        return obj


def convert_to_snake_case(obj):
    """
    Recursively converts dictionary keys from camelCase to snake_case.

    Args:
        obj: The object to convert. Can be a dict, list, or other type.

    Returns:
        The converted object with all dictionary keys in snake_case.
    """

    def format_snake_case(camel_str: str) -> str:
        """
        Converts a camelCase string to snake_case.

        Args:
            camel_str (str): The camelCase string to convert.

        Returns:
            str: The converted snake_case string.
        """
        # Insert an underscore before each capital letter and convert to lowercase.
        snake_str = re.sub(r'(?<!^)(?=[A-Z])', '_', camel_str).lower()
        return snake_str

    # Check if the object is a list.
    if isinstance(obj, list):
        # Recursively convert each item in the list.
        return [convert_to_snake_case(item) for item in obj]
    # Check if the object is a dictionary.
    elif isinstance(obj, dict):
        # Create a new dictionary to store converted keys and values.
        new_dictionary = {}
        for key, value in obj.items():
            # Convert the key to snake_case.
            new_key = format_snake_case(key)
            # Recursively convert the value.
            new_dictionary[new_key] = convert_to_snake_case(value)
        return new_dictionary
    else:
        # Return the object as is if it's neither a list nor a dict.
        return obj


def load_plugins(manifests_path: str) -> dict:
    """
    Loads plugin manifests from a directory and organizes them by plugin type.

    Args:
        manifests_path (str): The path to the directory containing plugin manifests.

    Returns:
        dict: A dictionary where keys are plugin types and values are dictionaries of plugins.
    """
    # Initialize the cache for plugins.
    plugins_cache = {}

    # Walk through the directory tree starting at manifests_path.
    for dir_path, dir_names, filenames in os.walk(manifests_path):
        for filename in filenames:
            # Skip files that are not JSON.
            if not filename.endswith('.json'):
                continue

            # Construct the full file path.
            file_path = os.path.join(dir_path, filename)
            with open(file_path, 'r') as opened_file:
                # Load the JSON content.
                content = json.load(opened_file)
                # Get the plugin type and name from the content.
                plugin_type = content.get('pluginType', '').lower()
                plugin_name = content.get('key')

                if plugin_type and plugin_name:
                    # Initialize the plugin type category if not already present.
                    if plugin_type not in plugins_cache:
                        plugins_cache[plugin_type] = {}
                    # Add the plugin to the cache.
                    plugins_cache[plugin_type][plugin_name] = content
    return plugins_cache


def mount_session(url: str, session_id: str) -> WebDriver:
    """
    Reconstructs a WebDriver session given the URL of the remote WebDriver server and a session ID.

    This function is useful when you need to reconnect to an existing WebDriver session,
    for example, after a crash or when reusing sessions for performance reasons.

    Args:
        url (str): The URL of the remote WebDriver server (e.g., "http://localhost:4444/wd/hub").
        session_id (str): The session ID of the existing WebDriver session to reconnect to.

    Returns:
        WebDriver: A WebDriver instance connected to the existing session.
    """
    # Backup the original WebDriver.execute method.
    execute = WebDriver.execute

    def local_executor(self, command, params=None):
        """
        Overrides the execute method to intercept the 'newSession' command.

        If the command is not 'newSession', it calls the original execute method.
        If the command is 'newSession', it returns a response with the provided session ID.
        """
        if command != "newSession":
            # Use the original execute method for all commands except 'newSession'.
            return execute(self, command, params)

        # Mimic a successful 'newSession' command by returning the existing session ID.
        return {'success': 0, 'value': {}, 'sessionId': session_id}

    # Override the WebDriver.execute method with the local executor.
    WebDriver.execute = local_executor

    # Initialize a new WebDriver instance using the overridden execute method.
    new_driver = webdriver.Remote(command_executor=url, options=Options())

    # Manually set the session ID to the existing session.
    new_driver.session_id = session_id

    # Restore the original WebDriver.execute method.
    WebDriver.execute = execute

    # Return the WebDriver instance connected to the existing session.
    return new_driver


def new_trace_id() -> str:
    """
    Generates a trace ID with the format 'PTNxxxxxxxxxx:00000001',
    where 'PTN' is a fixed prefix, followed by random alphanumeric characters,
    and an 8-digit zero-padded number after the colon.

    Returns:
        str: The generated trace ID.
    """
    prefix = "PTN"

    # Number of random characters after 'PTN'.
    random_length = 10
    # Generate a string of random uppercase letters and digits.
    random_chars = ''.join(
        secrets.choice(string.ascii_uppercase + string.digits) for _ in range(random_length)
    )

    # Generates a number between 0 and 99,999,999.
    number = secrets.randbelow(100000000)

    # Formats the trace ID with the generated values.
    trace_id = f"{prefix}{random_chars}:{number:08d}"

    # Returns the generated trace ID with the format 'PTNxxxxxxxxxx:00000001'.
    return trace_id
