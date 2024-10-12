import json
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional


class PluginResponseModel:
    """
    A model representing the response of a plugin operation, containing parameters, exceptions, and extractions.

    Attributes:
        application_parameters (Dict[str, str]): A dictionary to hold application-specific parameters.
        session_parameters (Dict[str, str]): A dictionary to hold session-specific parameters.
        exceptions (List[G4ExceptionModel]): A list of exceptions encountered during plugin execution.
        extractions (List[G4ExtractionModel]): A list of extractions performed by the plugin.
    """

    def __init__(self):
        """
        Initializes a new instance of PluginResponseModel with empty dictionaries for parameters and empty lists for
        exceptions and extractions.
        """
        self.application_parameters: Dict[str, str] = {}
        self.data_provider: [Dict[str, Any]] = []
        self.entity: Dict[str, Any] = {}
        self.exceptions: List[G4ExceptionModel] = []
        self.extractions: List[G4ExtractionModel] = []
        self.session_parameters: Dict[str, str] = {}

    @staticmethod
    def from_json(json_str: str) -> 'PluginResponseModel':
        """
        Creates an instance of PluginResponseModel from a JSON string.

        Args:
            json_str (str): A JSON-encoded string representing the plugin response.

        Returns:
            PluginResponseModel: A model object populated with data from the JSON string.

        Raises:
            ValueError: If the input is not a valid JSON string.
        """
        try:
            # Parse the JSON string into a dictionary
            data = json.loads(json_str)

            # Convert the dictionary into a PluginResponseModel instance
            return PluginResponseModel.from_dict(data)

        except json.JSONDecodeError as e:
            # Raise a ValueError if the JSON string is invalid
            raise ValueError(f"Invalid JSON data: {e}") from e

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'PluginResponseModel':
        """
        Creates an instance of PluginResponseModel from a dictionary.

        Args:
            data (Dict[str, Any]): A dictionary containing the plugin response data.

        Returns:
            PluginResponseModel: A model object populated with the provided data.
        """
        # Initialize a new PluginResponseModel object
        response = PluginResponseModel()

        # Convert and populate the exceptions and extractions lists from the data
        response.data_provider = data.get("dataProvider", [])
        response.entity = data.get("entity", {})
        response.exceptions = [G4ExceptionModel(**exception) for exception in data.get("exceptions", [])]
        response.extractions = [G4ExtractionModel(**extraction) for extraction in data.get("extractions", [])]

        # Populate application and session parameters from the data
        response.application_parameters = data.get("applicationParameters", {})
        response.session_parameters = data.get("sessionParameters", {})

        return response

    def to_dict(self) -> Dict[str, Any]:
        """
        Converts the PluginResponseModel instance into a dictionary.

        Returns:
            Dict[str, Any]: A dictionary representation of the model.
        """
        return {
            "applicationParameters": self.application_parameters,
            "dataProvider": self.data_provider,
            "entity": self.entity,
            "exceptions": self.exceptions,
            "extractions": self.extractions,
            "sessionParameters": self.session_parameters
        }

    def __str__(self) -> str:
        """
        Returns a JSON-formatted string representation of the model.

        Returns:
            str: A pretty-printed JSON string representing the model's data.
        """
        # Convert the model to a dictionary and format it as a pretty JSON string
        return json.dumps(self.to_dict(), indent=4)


@dataclass
class G4EntityModel:
    """Describes a contract for receiving G4 entity information from G4 service."""
    content: Dict[str, Any] = field(default_factory=dict)
    iteration: int = 0


@dataclass
class G4ExceptionModel:
    """Describes a contract for receiving G4 exceptions data."""
    plugin_name: Optional[str] = None
    reference: Any = None
    repeat_reference: int = 0
    reason_phrase: str = ''
    screenshots: Optional[str] = None


@dataclass
class G4SessionModel:
    """Describes a contract for receiving G4Session information from G4™ Service."""
    id: str = ''
    machine_ip: str = ''
    machine_name: str = ''

    def __init__(self, session_id: str = '', machine_ip: str = '', machine_name: str = ''):
        self.id = session_id
        self.machine_ip = machine_ip
        self.machine_name = machine_name


@dataclass
class G4ExtractionModel:
    """Represents a model for G4 extraction."""
    entities: List[G4EntityModel] = field(default_factory=list)
    key: Optional[str] = None
    reference: Any = None
    session: Optional[G4SessionModel] = None
