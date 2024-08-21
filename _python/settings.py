import pathlib
import json
import yaml


THIS_FILE_DIR = pathlib.Path(__file__).parent
MAIN_PROJECT_DIR = THIS_FILE_DIR.parent
CONFIG_FILE_NAME = "config.yaml"

# ============================================================


def get_main_project_dir():
    return str(MAIN_PROJECT_DIR)


def get_config_file_path():
    config_file_path = str(f"{THIS_FILE_DIR}/{CONFIG_FILE_NAME}")
    return config_file_path


def get_config_data():
    config_file_path = get_config_file_path()
    with open(config_file_path, "r") as f:
        if CONFIG_FILE_NAME.endswith(".yaml"):
            config_data = yaml.safe_load(f)
        elif CONFIG_FILE_NAME.endswith(".json"):
            config_data = json.load(f)
    return config_data
