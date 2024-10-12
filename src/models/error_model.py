from typing import Dict, List, Any
import json


class ErrorModel:
    def __init__(
        self,
        status: int,
        trace_id: str,
        errors: Dict[str, List[str]],
        request: Any,
        route_data: Dict[str, Any]
    ):
        """
        Initializes the ErrorModel instance with provided values.

        Args:
            status (int): The HTTP status code of the response.
            trace_id (str): A unique identifier for tracing the request.
            errors (Dict[str, List[str]]): A dictionary containing error messages categorized by keys.
            request (str): The HTTP request information.
            route_data (Dict[str, Any]): Additional routing data related to the request.
        """
        self.status = status
        self.trace_id = trace_id
        self.errors = errors
        self.request = request
        self.route_data = route_data

        # Perform post-initialization validations
        self.__post_init__()

    @staticmethod
    def from_json(json_str: str) -> 'ErrorModel':
        """
        Creates an ErrorModel instance from a JSON-formatted string.

        Args:
            json_str (str): A JSON-formatted string representing the API response.

        Returns:
            ErrorModel: An instance of ErrorModel populated with the provided JSON data.

        Raises:
            ValueError: If the JSON string cannot be parsed or is invalid.
        """
        try:
            data = json.loads(json_str)
            return ErrorModel.from_dict(data)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON data: {e}") from e

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'ErrorModel':
        """
        Creates an ErrorModel instance from a dictionary.

        Args:
            data (Dict[str, Any]): A dictionary representing the API response.

        Returns:
            ErrorModel: An instance of ErrorModel populated with the provided data.
        """
        return ErrorModel(
            status=data.get("status", 0),
            trace_id=data.get("traceId", ""),
            errors=data.get("Errors", {}),
            request=data.get("Request", ""),
            route_data=data.get("RouteData", {})
        )

    def to_dict(self) -> Dict[str, Any]:
        """
        Converts the ApiResponse instance back to a dictionary with original JSON key names.

        Returns:
            Dict[str, Any]: A dictionary representation of the ApiResponse with original keys.
        """
        return {
            "status": self.status,
            "traceId": self.trace_id,
            "errors": self.errors,
            "request": self.request,
            "routeData": self.route_data
        }

    def __str__(self) -> str:
        """
        Returns the JSON string representation of the ApiResponse instance.

        Returns:
            str: A JSON-formatted string representing the ApiResponse.
        """
        return json.dumps(self.to_dict(), indent=4)

    def __post_init__(self):
        """
        Post-initialization processing to ensure that all fields are correctly set.
        """
        # Ensure that 'errors' is a dictionary
        if not isinstance(self.errors, dict):
            raise ValueError("errors must be a dictionary with string keys and list of string values.")

        # Ensure that 'route_data' is a dictionary
        if not isinstance(self.route_data, dict):
            raise ValueError("route_data must be a dictionary.")

        # Validate that each error key maps to a list of strings
        for key, messages in self.errors.items():
            if not isinstance(messages, list):
                raise ValueError(f"Error messages for '{key}' must be a list of strings.")
            for message in messages:
                if not isinstance(message, str):
                    raise ValueError(f"Each error message under '{key}' must be a string.")
