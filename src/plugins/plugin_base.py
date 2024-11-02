from abc import ABC, abstractmethod

from models.plugin_response_model import PluginResponseModel, G4ExceptionModel
from models.setup_model import SetupModel

import traceback


class PluginBase(ABC):
    def __init__(self, plugin_setup_model: SetupModel):
        self.plugin_setup_model = plugin_setup_model

    @abstractmethod
    def on_send(self, action_request) -> PluginResponseModel:
        """
        Abstract method for sending an action request. This method must be
        implemented by subclasses to define the specific behavior of sending
        the action request.

        Parameters:
            action_request (ActionRequest): The request object containing
                                            the details needed to perform the action.

        Returns:
            PluginResponseModel: A response object that contains the result of
                                 the action request processing.

        Raises:
            Any relevant exceptions that subclasses might need to handle
            should be documented here.
        """
        pass

    def send(self, action_request) -> PluginResponseModel:
        """
        Sends an action request and handles any exceptions that may occur.

        Parameters:
            action_request (ActionRequest): The request object containing information about the action to be executed.

        Returns:
            PluginResponseModel: A response object with the result of the send operation or an error model
            if an exception occurs.
        """
        try:
            # Attempt to process the action request using the on_send method
            return self.on_send(action_request)

        except Exception as e:
            # Create an exception model to capture error details
            exception_model = G4ExceptionModel()

            # Populate the exception model with relevant information from the action request
            exception_model.data = {
                'message': str(e),
                'stackTrace': traceback.format_exc()
            }
            exception_model.plugin_name = action_request.get('entity', {}).get('pluginName', 'ExternalPlugin')
            exception_model.message = str(e)
            exception_model.reference = action_request.get('entity', {}).get('reference', None)
            exception_model.iteration = action_request.get('entity', {}).get('iteration', 0)
            exception_model.type = type(e).__name__

            # Prepare a response model to return the exception
            response = PluginResponseModel()
            response.exceptions.append(exception_model)

            # Return the response model containing the exception information
            return response
