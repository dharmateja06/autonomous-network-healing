import time

from monitoring.alarm import create_alarm, print_alarm
from kafka_producer import publish_alarm


LINKS = {
    "R1-R2": ("clab-anh-r1", "10.0.12.2"),
    "R1-R3": ("clab-anh-r1", "10.0.13.2"),
    "R2-R3": ("clab-anh-r2", "10.0.23.2"),
}


HEALING_DEVICES = {
    "R1-R2": ("r1", "eth1"),
    "R1-R3": ("r1", "eth2"),
    "R2-R3": ("r2", "eth2"),
}


def ping(container, ip_address):
    import subprocess

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
            ip_address,
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    return result.returncode == 0


def check_links():
    states = {}

    for link_name, (container, destination_ip) in LINKS.items():

        if ping(container, destination_ip):
            states[link_name] = "UP"
        else:
            states[link_name] = "DOWN"

        print(f"{link_name} : {states[link_name]}")

    return states


def handle_fault(link_name):
    device, interface = HEALING_DEVICES[link_name]

    alarm = create_alarm(
        link=link_name,
        device=device,
        interface=interface,
        fault_type="INTERFACE_DOWN",
        severity="CRITICAL",
    )

    print_alarm(alarm)

    try:
        publish_alarm(alarm)
    except Exception as error:
        print("\nKAFKA PUBLISH FAILED")
        print(f"Reason: {error}")


print("\n========================================")
print("     AUTONOMOUS NETWORK MONITOR")
print("========================================")

previous_states = check_links()

print("\nMonitoring started...")

while True:

    time.sleep(5)

    print("\n--- Network Health Check ---")

    current_states = check_links()

    for link_name in LINKS:

        previous = previous_states[link_name]
        current = current_states[link_name]

        if previous == "UP" and current == "DOWN":

            print(
                f"\nALARM: {link_name} changed "
                f"from UP to DOWN"
            )

            handle_fault(link_name)

        elif previous == "DOWN" and current == "UP":

            print(
                f"\nRECOVERY: {link_name} "
                f"changed from DOWN to UP"
            )

    previous_states = current_states
