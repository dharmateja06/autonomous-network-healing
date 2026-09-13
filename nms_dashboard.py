import subprocess
import os
from datetime import datetime


ROUTERS = {
    "r1": "clab-anh-r1",
    "r2": "clab-anh-r2",
    "r3": "clab-anh-r3",
}


LINKS = {
    "R1-R2": {
        "router": "r1",
        "interface": "eth1",
        "target": "10.0.12.2",
    },
    "R1-R3": {
        "router": "r1",
        "interface": "eth2",
        "target": "10.0.13.2",
    },
    "R2-R3": {
        "router": "r2",
        "interface": "eth2",
        "target": "10.0.23.2",
    },
}


def interface_state(router, interface):
    container = ROUTERS[router]

    result = subprocess.run(
        [
            "docker",
            "exec",
            container,
            "cat",
            f"/sys/class/net/{interface}/operstate",
        ],
        capture_output=True,
        text=True,
    )

    return result.stdout.strip()


def check_connectivity(router, target):
    container = ROUTERS[router]

    result = subprocess.run(
        [
            "docker",
            "exec",
            container,
            "ping",
            "-c",
            "1",
            "-W",
            "1",
            target,
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    return result.returncode == 0


def show_dashboard():

    os.system("clear")

    print("=" * 60)
    print("          AUTONOMOUS NETWORK HEALING PLATFORM")
    print("                    NMS STATUS")
    print("=" * 60)

    print(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    print("\nNETWORK LINKS")
    print("-" * 60)

    for link_name, details in LINKS.items():

        router = details["router"]
        interface = details["interface"]
        target = details["target"]

        state = interface_state(router, interface)

        if state == "up" and check_connectivity(router, target):
            status = "UP"
        else:
            status = "DOWN"

        print(
            f"{link_name:<10} | "
            f"{router} {interface:<5} | "
            f"STATUS: {status}"
        )

    print("\nROUTER STATUS")
    print("-" * 60)

    for router, container in ROUTERS.items():

        result = subprocess.run(
            [
                "docker",
                "inspect",
                "-f",
                "{{.State.Running}}",
                container,
            ],
            capture_output=True,
            text=True,
        )

        state = result.stdout.strip()

        if state == "true":
            status = "RUNNING"
        else:
            status = "DOWN"

        print(f"{router.upper():<10} | STATUS: {status}")

    print("\nRECENT HEALING EVENTS")
    print("-" * 60)

    log_file = "logs/healing.log"

    if os.path.exists(log_file):

        with open(log_file, "r") as file:
            lines = file.readlines()

        if lines:

            for line in lines[-5:]:
                print(line.strip())

        else:
            print("No healing events recorded.")

    else:
        print("Healing log not found.")

    print("\n" + "=" * 60)
    print("NMS STATUS VIEW COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    show_dashboard()
