# infra/data_reader.py

import yaml
import os

# Define the root directory relative to this script
ROOT_DIR = os.path.join(os.path.dirname(__file__), '..')


def read_yaml_data(path_segments: list):
    """
    Reads a YAML file by constructing the path from a list of segments.

    Args:
        path_segments: List of directory/file names relative to the project root.

    Returns:
        dict: The content of the YAML file.

    Raises:
        FileNotFoundError: If the file does not exist.
    """

    # Example path_segments: ['data', 'organization', 'sites_locations.yaml']
    file_path = os.path.join(ROOT_DIR, *path_segments)

    try:
        with open(file_path, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError as e:
        raise FileNotFoundError(f"Data file not found at: {file_path}") from e
    except yaml.YAMLError as e:
        # Handle potential YAML parsing errors
        raise ValueError(f"Error parsing YAML file {file_path}: {e}") from e
