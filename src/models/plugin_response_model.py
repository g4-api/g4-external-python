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

        This method iterates over any exceptions and extractions associated with the
        PluginResponseModel instance, converting each one to a dictionary format to allow
        for easy serialization or further processing.

        Returns:
            Dict[str, Any]: A dictionary representation of the model, including:
                - applicationParameters: Application-specific parameters.
                - dataProvider: Data provider details.
                - entity: Information about the entity involved in the response.
                - exceptions: List of exception details, converted to dictionaries.
                - extractions: List of extraction details, converted to dictionaries.
                - sessionParameters: Session-specific parameters.
        """

        # Initialize an empty list to store converted exceptions
        exceptions = []

        # Convert each exception in the list to a dictionary and add to exceptions list
        for exception in self.exceptions:
            exceptions.append(exception.__dict__())

        # Initialize an empty list to store converted extractions
        extractions = []

        # Convert each extraction in the list to a dictionary and add to extractions list
        for extraction in self.extractions:
            extractions.append(extraction.__dict__())

        # Return a dictionary containing all attributes of PluginResponseModel
        return {
            "applicationParameters": self.application_parameters,
            "dataProvider": self.data_provider,
            "entity": self.entity,
            "exceptions": exceptions,
            "extractions": extractions,
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
    data: [Dict[str, Any]] = field(default_factory=dict)
    iteration: int = 0
    plugin_name: Optional[str] = None
    reference: Any = None
    reason_phrase: str = ''
    screenshot: Optional['ScreenshotModel'] = None
    type: Optional[str] = None

    # Convert the G4ExceptionModel instance to a dictionary
    def __dict__(self):
        return {
            "data": self.data,
            "iteration": self.iteration,
            "pluginName": self.plugin_name,
            "reference": self.reference,
            "reasonPhrase": self.reason_phrase,
            "screenshot": self.screenshot,
            "type": self.type
        }


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

    def __dict__(self):
        return {
            "id": self.id,
            "machineIp": self.machine_ip,
            "machineName": self.machine_name
        }


@dataclass
class G4ExtractionModel:
    """Represents a model for G4 extraction."""
    entities: List[G4EntityModel] = field(default_factory=list)
    key: Optional[str] = None
    reference: Any = None
    session: Optional[G4SessionModel] = None

    # Convert the G4ExtractionModel instance to a dictionary
    def __dict__(self):
        return {
            "entities": self.entities,
            "key": self.key,
            "reference": self.reference,
            "session": self.session.__dict__()
        }


@dataclass
class ScreenshotModel:
    """Describes a contract for receiving screenshot data."""
    name: str = ''
    data: str = ''
