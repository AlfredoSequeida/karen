import json
import os
import subprocess
import sys


def create_config():
    """
    create config file if it does not exist
    """

    config_file = "config.json"

    default_config = {
        "settings": {"names": ["karen", "kevin"], "lang": "en"},
        "addons": [],
    }

    if not os.path.exists(config_file):
        with open(config_file, "w") as config:
            json.dump(default_config, config)


def load_config(config_file_path: str) -> dict:
    """
    load json
    config_file_path: the file path of the config file
    """

    config_dict = None

    with open(config_file_path) as config:
        config_dict = json.load(config)

    return config_dict


def check_global_config(config_path: str):
    """
    simple check for the main (global) json config file to check for some
    requeired settings

    config_path: the file path of the config file
    """

    config = load_config(config_path)
    required_settings = ["names", "lang"]

    for setting in required_settings:
        if setting not in config["settings"]:
            print(f"Required setting '{setting}' missing from config")
            exit()


def check_addon_config(config: dict):
    """
    simple check for an addon json config file to check for some
    requeired settings

    config: the addon config
    """

    addon_name = config["name"]
    valid_keys = [
        "name",
        "commands",
        "entry-point",
        "languages",
        "required_packages",
        "settings",
        "version",
        "developer",
        "upstream",
    ]

    for key in config:
        if key not in valid_keys:
            print(f"invalid key '{key}' in {addon_name}'s config")
            exit()


def get_addon_configs(addons_dir: str) -> list:
    """
    get all the addon configs

    addons_dir: the directory where addons are stored
    """

    return [
        load_config(os.path.join(subdir, file))
        for subdir, dirs, files in os.walk(addons_dir)
        for file in files
        if file == "config.json"
    ]


def append_to_config(
    config_file_path: str, config_append: dict, key_name: str
):
    """
    append data to config file

    config_file_path: the path for the config file
    config_append: the setting to append to a config file
    key_name: the name of the config setting
    """

    config = load_config(config_file_path)
    config[key_name] = config_append

    with open(config_file_path, "w") as config_file:
        json.dump(config, config_file, indent=2)


def load_addons(config_file_path: str, addons_dir: str):
    """
    load addons to main config

    config_file_path: the main config file to load the addons to
    addons_dir: the directory where addons are store
    """

    addon_configs = get_addon_configs(addons_dir)

    # update addon settings if necessary
    config = load_config(config_file_path)

    for installed_addon in config["addons"]:
        try:
            for setting_key, setting_value in installed_addon[
                "settings"
            ].items():
                for addon_index in range(len(addon_configs)):
                    if (
                        addon_configs[addon_index]["name"]
                        == installed_addon["name"]
                    ):

                        addon_configs[addon_index]["settings"][
                            setting_key
                        ] = setting_value
        except:
            pass

    append_to_config(config_file_path, addon_configs, "addons")
