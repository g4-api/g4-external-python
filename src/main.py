import os
import tomllib

from flask import jsonify, request, Flask

from models.error_model import ErrorModel
from models.setup_model import SetupModel
from plugins.plugin_base import PluginBase
from utilities.common import new_trace_id, mount_session
from utilities.plugin_factory import PluginFactory

# Initialize the Flask application.
app = Flask(__name__)

# Initialize the plugins cache by loading plugins from the manifests directory.
# Load the plugins into the cache when the application starts.
plugins_cache = PluginFactory.initialize_manifest_cache()


@app.route('/api/v4/g4/plugins', methods=['GET'])
def get_plugins():
    """
    Retrieves all plugin manifests from the plugins cache.

    This endpoint returns a list of all plugin manifests that have been loaded
    and cached. It handles the retrieval process and returns them as a JSON response.

    Returns:
        Response: A JSON response containing a list of all plugin manifests.
                  If an error occurs, returns a 404 status code.
    """
    try:
        # Initialize an empty list to hold all the manifests
        manifests = []

        # Loop through the cache of plugins organized by plugin type
        for plugin_type, cache_models in plugins_cache.items():
            # Loop through each cached model for the given plugin type
            for class_name, cache_model in cache_models.items():
                # Append the manifest associated with the current cache model to the list
                manifests.append(cache_model['manifest'])

        # Return the list of manifests as a JSON response
        return jsonify(manifests)

    except Exception as e:
        # Log the error for debugging purposes
        print(f"Error retrieving plugins: {e}")

        # Return a 404 status response in case of any error
        return app.response_class(status=404)


@app.route('/api/v4/g4/plugins/type/<plugin_type>/key/<plugin_name>', methods=['GET'])
def get_plugin_by_type_and_key(plugin_type, plugin_name):
    """
    Retrieves a specific plugin manifest by its type and key.

    Args:
        plugin_type (str): The type of the plugin.
        plugin_name (str): The key (class name) of the plugin.

    Returns:
        Response: A JSON response containing the plugin manifest if found,
                  otherwise a 404 status response if the plugin does not exist.
    """
    try:
        # Convert plugin type and name to lowercase for case-insensitive comparison
        plugin_type = plugin_type.lower()
        plugin_name = plugin_name.lower()

        # Check if the plugin type and name exist in the cache
        if plugin_type in plugins_cache and plugin_name in plugins_cache[plugin_type]:
            # Retrieve the manifest associated with the plugin type and name
            manifest = plugins_cache[plugin_type][plugin_name]["manifest"]

            # Return the manifest as a JSON response
            return jsonify(manifest)
        else:
            # Return 404 status if the plugin is not found in the cache
            return app.response_class(status=404)

    except Exception as e:
        # Log the error for debugging purposes
        print(f"Error retrieving plugin {plugin_name} of type {plugin_type}: {e}")

        # Return 404 status in case of an error
        return app.response_class(status=404)


@app.route('/api/v4/g4/plugins/<plugin_name>', methods=['GET'])
def get_plugin(plugin_name):
    """
    Retrieves a specific plugin manifest by its name.

    Args:
        plugin_name (str): The name of the plugin (key/class name) to retrieve.

    Returns:
        Response: A JSON response containing the plugin manifest if found,
                  otherwise returns a 404 status response if the plugin does not exist.
    """
    try:
        # Convert plugin name to lowercase for case-insensitive comparison
        plugin_name = plugin_name.lower()

        # Iterate over the cached plugin types and their associated plugin classes
        for plugin_type, plugin_classes in plugins_cache.items():
            # Check if the plugin name exists in the current plugin type's classes
            if plugin_name in plugin_classes:
                # Return the manifest of the found plugin
                return jsonify(plugin_classes[plugin_name]["manifest"])

        # If plugin is not found, return 404 status
        return app.response_class(status=404)

    except Exception as e:
        # Log the error message for debugging purposes
        print(f"Error retrieving plugin {plugin_name}: {e}")

        # Return 404 status in case of an error
        return app.response_class(status=404)


@app.route('/api/v4/g4/plugins/<plugin_type>/invoke', methods=['POST'])
def invoke(plugin_type):
    """
    API endpoint to invoke a plugin based on its type and name.

    Args:
        plugin_type (str): The type of the plugin to be invoked, extracted from the URL.

    Returns:
        Response: JSON response from the plugin invocation or 404 error if plugin is not found.
    """
    # Parse the incoming JSON request
    plugin_request = request.json

    # Ensure 'pluginName' exists in the request entity
    if 'entity' not in plugin_request or 'pluginName' not in plugin_request['entity']:
        return app.response_class(status=404)

    # Extract the class name and convert to lowercase
    class_name = f"{plugin_request['entity']['pluginName']}".lower()

    # Convert plugin type to lowercase for consistency
    plugin_type = plugin_type.lower()

    # Ensure 'driverUrl' and 'session' are present in the request
    if 'driverUrl' not in plugin_request or 'session' not in plugin_request:
        return app.response_class(status=404)

    # Extract driver URL and session ID from the request
    driver_url = plugin_request['driverUrl']
    session_id = plugin_request['session']

    # Mount session using driver URL and session ID
    driver = mount_session(driver_url, session_id)

    # Create a SetupModel instance and assign the driver
    setup_model = SetupModel()
    setup_model.driver = driver

    # Check if the plugin type exists in the cache
    if plugin_type not in plugins_cache:
        return app.response_class(status=404)

    # Check if the class name exists under the plugin type in the cache
    if class_name not in plugins_cache[plugin_type]:
        return app.response_class(status=404)

    # Retrieve the plugin class from the cache
    plugin_class = plugins_cache[plugin_type][class_name]['class']

    # Ensure the plugin class inherits from PluginBase
    if not issubclass(plugin_class, PluginBase):
        return app.response_class(status=404)

    # Instantiate the plugin class with the setup model
    plugin_instance: PluginBase = plugin_class(setup_model)

    # Invoke the plugin with the provided request and convert the result to a dictionary
    response = plugin_instance.invoke(plugin_request).to_dict()

    # Return the JSON response
    return jsonify(response)


@app.errorhandler(500)
def internal_error(error):
    """
    Handles internal server errors (HTTP 500).

    Constructs an ErrorModel with details about the error and returns it as JSON.

    Args:
        error: The error object.

    Returns:
        Response: A JSON response containing the error details, with HTTP status code 500.
    """
    # Create an ErrorModel instance with error details.
    error500 = ErrorModel(
        status=500,
        route_data={"method": request.method, "path": request.path},
        trace_id=new_trace_id(),
        errors={"error": [f"{error}"]},
        request=None
    )

    # Return the error model as JSON with a 500 status code.
    return jsonify(error500), 500


if __name__ == '__main__':
    # Load configuration from TOML file.
    config_path = os.path.join(os.path.dirname(__file__), 'config.toml')
    with open(config_path, 'rb') as f:
        # Load the TOML configuration file.
        toml_config = tomllib.load(f)

    # Apply server configurations from the loaded TOML file.
    host = toml_config['server']['host']
    port = toml_config['server']['port']
    debug = toml_config['server']['debug']

    # Run the application with loaded configurations.
    app.run(host=host, port=port, debug=debug, use_reloader=False)
