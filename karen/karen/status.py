from subprocess import Popen, PIPE
import argparse

"""
get voice assistant status
"""


def is_online() -> bool:
    """
    check if voice assistant is online
    """

    is_online = False

    process = "karen.py"
    instance = "python"

    proc1 = Popen(["ps", "auxf"], stdout=PIPE)
    proc2 = Popen(
        ["grep", process],
        stdin=proc1.stdout,
        stdout=PIPE,
        stderr=PIPE,
    )

    proc1.stdout.close()
    out, err = proc2.communicate()

    for line in out.decode("utf8").splitlines():
        line = line.lower()
        if instance in line and process in line:
            is_online = True

    return is_online


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="check status")
    parser.add_argument(
        "--online",
        "-o",
        action="store_true",
        help="check active/online status",
    )

    args = parser.parse_args()

    if args.online:
        print(is_online())