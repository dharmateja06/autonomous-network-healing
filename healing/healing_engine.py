from netconf.netconf_adapter import set_interface
import subprocess
import time
import sys
from datetime import datetime


HEALING_ACTIONS = {
    "R1-R2": ("r1", "eth1"),
    "R1-R3": ("r1", "eth2"),
    "R2-R3": ("r2", "eth2"),
}


ROUTERS = {
    "r1": "clab-anh-r1",
    "r2": "clab-anh-r2",
    "r3": "clab-anh-r3",
}


PING_TARGETS = {
    "R1-R2": ("clab-anh-r1", "10.0.12.2"),
    "R1-R3": ("clab-anh-r1", "10.0.13.2"),
    "R2-R3": ("clab-anh-r2", "10.0.23.2"),
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


def verify_connectivity(link_name):
    container, target_ip = PING_TARGETS[link_name]

    print(f"\n{link_name}: verifying connectivity...")

    result = subprocess.run(
        [
            "docker",
            "exec",
            container,
            "ping",
            "-c",
            "3",
            "-W",
            "1",
            target_ip,
        ],
        capture_output=True,
        text=True,
    )

    if result.returncode == 0:
        print(f"{link_name}: CONNECTIVITY VERIFIED")
        return True

    print(f"{link_name}: CONNECTIVITY VERIFICATION FAILED")

    return False


def log_healing_event(
    link_name,
    router,
    interface,
    attempt,
    result,
):
    timestamp = datetime.now().isoformat()

    with open("logs/healing.log", "a") as log_file:
        log_file.write(
            f"{timestamp} | "
            f"link={link_name} | "
            f"router={router} | "
            f"interface={interface} | "
            f"attempt={attempt} | "
            f"result={result}\n"
        )


def heal_link(link_name):

    if link_name not in HEALING_ACTIONS:
        print(f"ERROR: Unknown link: {link_name}")
        return False

    router, interface = HEALING_ACTIONS[link_name]

    max_attempts = 3

    for attempt in range(1, max_attempts + 1):

        print("\n========================================")
        print(
            f"       HEALING ATTEMPT {attempt}/{max_attempts}"
        )
        print("========================================")

        state = interface_state(
            router,
            interface,
        )

        print(
            f"{link_name}: current state = {state}"
        )

        # Case 1: Interface is already UP
        if state == "up":

            print(
                f"{link_name}: Interface already UP."
            )

            if verify_connectivity(link_name):

                print(
                    f"{link_name}: HEALING SUCCESSFUL"
                )

                log_healing_event(
                    link_name,
                    router,
                    interface,
                    attempt,
                    "SUCCESS",
                )

                return True

            print(
                f"{link_name}: Connectivity verification failed."
            )

        # Case 2: Interface is DOWN
        else:

            print(
                f"{link_name}: Fault detected."
            )

            print(
                f"{link_name}: Starting NETCONF healing..."
            )

            try:

                set_interface(
                    router=router,
                    interface=interface,
                    enabled=True,
                )

                time.sleep(2)

                new_state = interface_state(
                    router,
                    interface,
                )

                if new_state != "up":

                    print(
                        f"{link_name}: Interface still DOWN "
                        f"after healing attempt."
                    )

                else:

                    print(
                        f"{link_name}: Interface restored."
                    )

                    if verify_connectivity(link_name):

                        print(
                            f"{link_name}: HEALING SUCCESSFUL"
                        )

                        log_healing_event(
                            link_name,
                            router,
                            interface,
                            attempt,
                            "SUCCESS",
                        )

                        return True

                    print(
                        f"{link_name}: Connectivity verification failed."
                    )

            except Exception as error:

                print(
                    f"{link_name}: Healing attempt failed."
                )

                print(
                    f"Reason: {error}"
                )

        # Retry if healing was not successful
        if attempt < max_attempts:

            print(
                f"\n{link_name}: Retrying healing..."
            )

            time.sleep(3)

    # All attempts failed
    print(
        f"\n{link_name}: AUTONOMOUS HEALING FAILED "
        f"AFTER {max_attempts} ATTEMPTS"
    )

    log_healing_event(
        link_name,
        router,
        interface,
        max_attempts,
        "FAILED",
    )

    return False


if __name__ == "__main__":

    if len(sys.argv) != 2:

        print(
            "Usage: python -m healing.healing_engine <link>"
        )

        print("\nAvailable links:")

        for link in HEALING_ACTIONS:
            print(f"  {link}")

        sys.exit(1)

    link = sys.argv[1]

    success = heal_link(link)

    if success:
        sys.exit(0)

    sys.exit(1)
