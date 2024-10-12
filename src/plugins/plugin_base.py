from abc import ABC, abstractmethod

from models.plugin_response_model import PluginResponseModel
from models.setup_model import SetupModel


class PluginBase(ABC):
    def __init__(self, plugin_setup_model: SetupModel):
        self.plugin_setup_model = plugin_setup_model

    @abstractmethod
    def invoke(self, action_request) -> PluginResponseModel:
        pass
