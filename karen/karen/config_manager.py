import argparse
import json

from utils.setup import load_config

"""
manage main (global) config file
"""

CONFIG_FILE = "config.json"


def write_config(config_file_path: str, config: dict):
    """
    save config changes by writing to the config file
    """

    with open(config_file_path, "w") as config_file:
        json.dump(config, config_file, indent=2)


def update_addon_setting(
    addon_name: str = "",
    developer_name: str = "",
    setting_name: str = "",
    setting_value: str = "",
):

    """
    update addon setting

    addon_name: name of addon for which to update it's settings
    developer_name: name of addon developer
    setting_name: name of the setting to update
    setting_value: value for setting
    """

    config = load_config(CONFIG_FILE)

    for index in range(len(config["addons"])):
        if config["addons"][index]["name"] == addon_name:
            config["addons"][index]["settings"][setting_name] = setting_value
            break

    # save changes
    write_config(CONFIG_FILE, config)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="config manager")
    parser.add_argument(
        "--addon",
        "-a",
        help="update addon by name",
    )
    parser.add_argument(
        "--developer",
        "-d",
        help="addon developer",
    )
    parser.add_argument(
        "--setting",
        "-s",
        help="addon setting",
    )
    parser.add_argument(
        "--value",
        "-v",
        help="value for update",
    )

    args = parser.parse_args()

    if args.addon:
        if not args.setting:
            parser.error("addon requires setting (--setting, -s)")
        elif not args.developer:
            parser.error("addon requires developer (--developer, -d)")
        elif not args.value:
            parser.error("setting update requrires value (--value, -v)")

        update_addon_setting(
            addon_name=args.addon,
            developer_name=args.developer,
            setting_name=args.setting,
            setting_value=args.value,
        )