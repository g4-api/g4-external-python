import importlib
import json
import os
from collections import defaultdict
from typing import Optional, Any

import inflection

from models import setup_model
from models.setup_model import SetupModel
from plugins.plugin_base import PluginBase


class PluginFactory:
    @staticmethod
    def initialize_manifest_cache(manifests_folder="manifests"):
        """
        Build a cache of plugin classes and their associated manifests.

        Args:
            manifests_folder (str): The folder where manifest JSON files are located. Defaults to "manifests".

        Returns:
            dict: A dictionary where the key is the plugin type and the value is another dictionary
            containing the plugin class name and its associated manifest data.
        """
        # Initialize the cache as a defaultdict of dictionaries
        cache = defaultdict(dict)

        # Walk through the manifests folder and subfolders
        for root, dirs, files in os.walk(manifests_folder):
            # Loop over each file in the current directory
            for file in files:
                # Skip files that are not JSON files
                if not file.endswith('.json'):
                    continue

                # Construct the full path to the JSON file
                file_path = os.path.join(root, file)

                # Load and parse the JSON manifest file
                with open(file_path, 'r') as f:
                    manifest = json.load(f)

                    # Extract the plugin class name (key) and plugin type (type) from the manifest
                    plugin_class_name = manifest.get("key")
                    plugin_type = manifest.get("pluginType")

                    # Skip the manifest if either 'key' or 'type' is missing
                    if not plugin_class_name or not plugin_type:
                        continue

                    # Retrieve the actual plugin class from the PluginFactory
                    plugin_class = PluginFactory.__find_plugin_class(plugin_class_name)

                    # Skip if the plugin class could not be found
                    if not plugin_class:
                        continue

                    # Store the plugin class and manifest data in the cache under the plugin type
                    cache[f'{plugin_type}'.lower()][f'{plugin_class_name}'.lower()] = {
                        "class": plugin_class,
                        "manifest": manifest
                    }

        # Return the fully built cache
        return cache

    @staticmethod
    def new_plugin(class_name: str, plugin_setup_model: SetupModel) -> Optional[PluginBase]:
        """
        Instantiates a new plugin class by finding the class based on its name and passing the setup model as
        an argument.

        Args:
            class_name (str): The name of the plugin class to instantiate.
            plugin_setup_model (setup_model): The setup model to pass as an argument when instantiating the plugin.

        Returns:
            Optional[PluginBase]: An instance of the plugin class if found and valid, otherwise None.
        """
        # Find the plugin class using the class name
        plugin_class = PluginFactory.__find_plugin_class(class_name)

        # Instantiate the plugin class with the setup model if found
        return plugin_class(plugin_setup_model) if plugin_class else None

    @staticmethod
    def __find_module_for_class(class_name, base_package="plugins"):
        """
        Finds the module that contains the class based on its name by searching in the base package directory.

        Args:
            class_name (str): The name of the class to find the module for.
            base_package (str): The base package to start searching from (default is "plugins").

        Returns:
            str: The full module path as a dot-separated string.

        Raises:
            ModuleNotFoundError: If the module corresponding to the class is not found.
        """
        # Convert class name to snake_case
        file_name = inflection.underscore(class_name) + ".py"

        # Start walking from the base package directory
        for root, dirs, files in os.walk(base_package):
            if file_name in files:
                # Get the full module path by replacing slashes with dots and removing .py
                module_path = os.path.join(root, file_name).replace(os.sep, '.').replace('.py', '')
                return module_path

        # Raise an exception if the class is not found in the base package directory or its subdirectories
        raise ModuleNotFoundError(f"Module for class {class_name} not found in {base_package} directory")

    @staticmethod
    def __find_plugin_class(class_name: str) -> Any:
        """
        Finds and validates a plugin class by dynamically importing its module and retrieving the class.

        Args:
            class_name (str): The name of the plugin class to find.

        Returns:
            Optional[PluginBase]: The plugin class if found and valid, otherwise None.

        Raises:
            TypeError: If the found class does not inherit from PluginBase.
        """
        try:
            # Find the module for the class
            module_name = PluginFactory.__find_module_for_class(class_name)

            # Dynamically import the module (full module path)
            module = importlib.import_module(module_name)

            # Retrieve the class from the module
            cls = getattr(module, class_name)

            # Check inheritance
            if not issubclass(cls, PluginBase):
                raise TypeError(f"{class_name} does not inherit from {PluginBase.__name__}")

            # Instantiate the class with arguments
            return cls
        except (ModuleNotFoundError, AttributeError) as e:
            print(f"Error: {e}")
            return None
