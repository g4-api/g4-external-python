from models.plugin_response_model import PluginResponseModel
from plugins.plugin_base import PluginBase


class ConvertToRoman(PluginBase):
    """
    A plugin that converts an integer to its Roman numeral representation.

    This plugin takes an integer value from the action request, converts it to a Roman numeral,
    and returns the result in a PluginResponseModel.

    Args:
        plugin_setup_model (SetupModel): The setup model which contains the necessary configurations.
    """

    def __init__(self, plugin_setup_model):
        """
        Initializes the ConvertToRoman plugin with the provided setup model.

        Args:
            plugin_setup_model (SetupModel): The setup model, including configurations like input values.
        """
        super().__init__(plugin_setup_model)  # Initialize the base class with the setup model

    def on_send(self, action_request) -> PluginResponseModel:
        """
        Converts an integer value to its Roman numeral equivalent.

        Args:
            action_request (dict): The action request containing arguments, including the value to convert.

        Returns:
            PluginResponseModel: A response model with the Roman numeral result stored in the 'MacroResult' key.
        """
        # Extract the integer value from the action request
        # Convert the value to an integer
        number = int(f"{action_request['arguments']['Number']}")

        # Lists of decimal values and their corresponding Roman numeral symbols
        values = [
            1000, 900, 500, 400,
            100, 90, 50, 40,
            10, 9, 5, 4,
            1
        ]
        symbols = [
            'M', 'CM', 'D', 'CD',
            'C', 'XC', 'L', 'XL',
            'X', 'IX', 'V', 'IV',
            'I'
        ]

        # Initialize an empty string to hold the Roman numeral result
        roman_num = ''

        # Index for iterating over the values and symbols lists
        i = 0

        # Loop to build the Roman numeral by subtracting values from num
        while number > 0:
            count = number // values[i]      # Determine how many times values[i] fits into num
            roman_num += symbols[i] * count  # Append the Roman numeral symbol corresponding to values[i]
            number -= values[i] * count      # Subtract the value from num
            i += 1                           # Move to the next Roman numeral symbol

        # Create the response model and store the Roman numeral result in the 'MacroResult' key
        response = PluginResponseModel()
        response.entity = {
            "MacroResult": roman_num
        }

        # Return the response model with the Roman numeral result
        return response
