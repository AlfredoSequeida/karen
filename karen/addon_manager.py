import argparse
import sys
import os
import json
import re
from subprocess import run, Popen, PIPE, check_output, check_call

from utils.setup import load_config, append_to_config, get_addon_configs


"""
manage addons for Linux system installations
"""

DOWNLOAD_LOCATION = "/tmp"
DOWNLOAD_DIR = "karen_addon"
ADDONS_DIR = "addons"


def github_url_is_valid(github_url: str) -> bool:
    """
    validate github project urls using regex

    github_url: the github project url
    """

    valid = False

    match = re.search(
        "^(https)(:\/\/)(github.com)[\/:]([^\/:]+)\/(.+)$", github_url
    )

    if match:
        valid = True

    return valid


def git_clone(github_url: str):
    """
    clone github projects uisng git clone

    github_url: the github project url
    """

    if github_url_is_valid(github_url):

        # remove existing addon to avoid conflicts with git clone
        run(["rm", "-r", "-f", f"{DOWNLOAD_LOCATION}/{DOWNLOAD_DIR}"])

        # download github project to tmp directory
        run(
            [
                "git",
                "clone",
                github_url,
                f"{DOWNLOAD_LOCATION}/{DOWNLOAD_DIR}",
            ]
        )


def get_installed_python_packages() -> list:
    """
    get all currently installed python packages
    """

    packages_output = check_output([sys.executable, "-m", "pip", "freeze"])

    return [
        package.split("==")[0]
        for package in packages_output.decode("utf-8").splitlines()
    ]


def install_python_package(package: str):
    """
    install PyPi packages using pip

    package: the package name
    """

    run([sys.executable, "-m", "pip", "install", package])


def install_required_packages(required_packages: list):
    """
    install addon required packages

    required_packages: the requried packages
    """
    installed_packages = get_installed_python_packages()

    for required_package in required_packages:
        # if package is not installed, then install that package
        if required_package not in installed_packages:
            install_python_package(required_package)


def add_upsteam_to_config(github_url: str, addon_package: str):
    """
    add upsteam url to addon config for reference

    github_url: the upstream github project url
    addon_package: the full pakcage identifier ('{developer}_{addon name}')
    """

    append_to_config(
        f"{ADDONS_DIR}/{addon_package}/config.json", github_url, "upstream"
    )


def create_addons_dir():
    """
    create addons directory if it does not exists
    """

    if not os.path.exists(ADDONS_DIR):
        os.makedirs(ADDONS_DIR)


def install_addon(config: dict, addon_package: str):
    """
    installing addon

    config: the downloaded addon config
    addon_package: the full pakcage identifier ('{developer}_{addon name}')
    """

    create_addons_dir()

    # recreate the project sturcture based on the app's config file to
    # minimize errors with project sturcture

    # install any required dependencies
    if "required_packages" in config:
        install_required_packages(config["required_packages"])

    try:
        run(["mkdir", f"{ADDONS_DIR}/{addon_package}"])
    except:
        pass

    run(f"mv {download_location}/* {ADDONS_DIR}/'{addon_package}'", shell=True)


def uninstall_python_package(package: str):
    """
    uninstall python package using pip

    package: the PyPi package name to uninstall
    """

    run([sys.executable, "-m", "pip", "uninstall", "-y", package])


def uninstall_required_packages(config: dict):
    """
    uninstall addon required packages using pip

    config: addon config
    """

    if "required_packages" in config:
        required_packages = config["required_packages"]

        for required_package in required_packages:
            uninstall_python_package(required_package)


def uninstall_addon(
    name: str = "",
    developer: str = "",
    uninstall_requirements: bool = False,
    config: dict = {},
):
    """
    uninstall addon required packages using pip

    config: addon config
    """

    # remove required packages
    if uninstall_requirements:
        uninstall_required_packages(config)

    # uninstall an addon by removing its directory
    run(["rm", "-r", "-f", f"{ADDONS_DIR}/{developer}_{name}"])


def restart():
    """
    restart voice assitant instance as background process using nohup
    """

    process = "Karen.py"
    instance = "python"

    proc1 = Popen(["ps", "auxf"], stdout=PIPE)
    proc2 = Popen(
        ["grep", process],
        stdin=proc1.stdout,
        stdout=PIPE,
        stderr=PIPE,
    )

    proc1.stdout.close()  # Allow proc1 to receive a SIGPIPE if proc2 exits.
    out, err = proc2.communicate()

    proc = None

    for line in out.decode("utf8").splitlines():
        if instance in line and process in line:
            proc = line.split()
            break

    try:
        # killing process by pid
        run(["kill", proc[1]])
    except:
        pass

    # restart process
    Popen(["nohup", "python3", "Karen.py"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="addon manager")
    parser.add_argument(
        "-i",
        "--install",
        help="install addon using github url",
    )
    parser.add_argument(
        "-u",
        "--uninstall",
        help="uninstall addon by name",
    )
    parser.add_argument(
        "--developer",
        "-d",
        help="addon developer",
    )
    parser.add_argument(
        "--requirements",
        "-r",
        action="store_true",
        default=False,
        help="uninstall addon requirements/dependencies",
    )

    args = parser.parse_args()

    if args.install:
        # removing .git from url if it exists
        args.install = args.install.replace(".git", "")

        try:
            git_clone(args.install)

            download_location = f"{DOWNLOAD_LOCATION}/{DOWNLOAD_DIR}"
            config = load_config(f"{download_location}/config.json")

            # setting package name

            # in order to decrease the posibility of dupliates, addons packages
            # follow this naming convention when installing
            # 'developer.addon name'

            # since "." in python is used to package directories, they are replaced
            # with underscores

            addon_package = (
                f"{config['developer'].replace('.', '_')}_{config['name']}"
            )

            install_addon(config, addon_package)
            add_upsteam_to_config(args.install, addon_package)
        except:
            pass
        finally:
            restart()

    elif args.uninstall:
        # checks for mutually inclusive args
        if not args.developer:
            parser.error("uninstall requires developer (--developer , -d)")

        addons = get_addon_configs(ADDONS_DIR)
        config = None

        for addon in addons:
            if addon["name"] == args.uninstall:
                config = addon
                break

        uninstall_addon(
            name=args.uninstall,
            developer=args.developer,
            uninstall_requirements=args.requirements,
            config=config,
        )

        restart()