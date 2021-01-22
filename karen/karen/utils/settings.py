from utils.setup import load_config

CONFIG_FILE = "config.json"


def get_addon_settings(addon_name: str) -> dict:
    """
    get settings for a specified addon

    addon_name: the name of the addon
    """

    addon_settings = None
    addons = load_config(CONFIG_FILE)["addons"]

    for addon in addons:
        if addon_name == addon["name"]:
            addon_settings = addon["settings"]
            break

    return addon_settings
