import sys
import subprocess


LINKS = {
    "R1-R2": ("r1", "eth1", "r2", "eth1"),
    "R1-R3": ("r1", "eth2", "r3", "eth2"),
    "R2-R3": ("r2", "eth2", "r3", "eth1"),
}


ROUTERS = {
    "r1": "clab-anh-r1",
    "r2": "clab-anh-r2",
    "r3": "clab-anh-r3",
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


def analyze_link(link_name):
    if link_name not in LINKS:
        print(f"ERROR: Unknown link {link_name}")
        return False

    router1, interface1, router2, interface2 = LINKS[link_name]

    state1 = interface_state(router1, interface1)
    state2 = interface_state(router2, interface2)

    print("\n========================================")
    print("        ROOT CAUSE ANALYSIS")
    print("========================================")

    print(f"Link       : {link_name}")
    print(f"{router1} {interface1}: {state1}")
    print(f"{router2} {interface2}: {state2}")

    if state1 != "up" or state2 != "up":
        print(f"\nROOT CAUSE: {link_name} interface failure")
        return True

    print("\nROOT CAUSE: No interface failure detected")
    return False


if __name__ == "__main__":

    if len(sys.argv) != 2:
        print("Usage: python rca_engine.py <link>")
        print("Example: python rca_engine.py R1-R2")
        sys.exit(1)

    link = sys.argv[1]

    fault_found = analyze_link(link)

    if fault_found:
        sys.exit(0)
    else:
        sys.exit(1)
