import os
import subprocess
from ncclient import manager


NETCONF_HOST = "127.0.0.1"
NETCONF_PORT = 830
NETCONF_USERNAME = "netconf"

ROUTERS = {
    "r1": "clab-anh-r1",
    "r2": "clab-anh-r2",
    "r3": "clab-anh-r3",
}


def get_password():
    password = os.getenv("NETCONF_PASSWORD")

    if not password:
        raise RuntimeError(
            "NETCONF_PASSWORD environment variable is not set."
        )

    return password


def send_netconf_config(router, interface, enabled):
    password = get_password()

    config = f"""
    <config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
      <interfaces xmlns="urn:anh:router">
        <interface>
          <name>{interface}</name>
          <enabled>{str(enabled).lower()}</enabled>
          <description>Autonomous healing interface</description>
        </interface>
      </interfaces>
    </config>
    """

    print("\nConnecting to NETCONF server...")

    with manager.connect(
        host=NETCONF_HOST,
        port=NETCONF_PORT,
        username=NETCONF_USERNAME,
        password=password,
        hostkey_verify=False,
        allow_agent=False,
        look_for_keys=False,
        timeout=10,
    ) as m:

        print("NETCONF CONNECTION SUCCESSFUL")

        reply = m.edit_config(
            target="running",
            config=config,
        )

        print("NETCONF CONFIGURATION APPLIED")
        print(reply.xml)


def apply_to_router(router, interface, enabled):
    if router not in ROUTERS:
        raise ValueError(f"Unknown router: {router}")

    if not interface.startswith("eth"):
        raise ValueError(f"Unsupported interface: {interface}")

    container = ROUTERS[router]
    state = "up" if enabled else "down"

    print(
        f"\nApplying configuration to actual router: "
        f"{router} {interface} -> {state}"
    )

    subprocess.run(
        [
            "docker",
            "exec",
            container,
            "ip",
            "link",
            "set",
            interface,
            state,
        ],
        check=True,
    )

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
        check=True,
    )

    actual_state = result.stdout.strip()

    print(
        f"Router verification: "
        f"{router} {interface} = {actual_state}"
    )

    expected_state = "up" if enabled else "down"

    if actual_state != expected_state:
        raise RuntimeError(
            f"Healing verification failed: "
            f"expected {expected_state}, got {actual_state}"
        )

    print("ROUTER CONFIGURATION VERIFIED")


def set_interface(router, interface, enabled):
    print("\n========================================")
    print("      NETCONF INTERFACE OPERATION")
    print("========================================")

    print(
        f"Target: {router} {interface}"
    )

    print(
        f"Requested state: "
        f"{'enabled' if enabled else 'disabled'}"
    )

    # Step 1: Store the desired state through NETCONF/YANG.
    send_netconf_config(
        router,
        interface,
        enabled,
    )

    # Step 2: Apply the state to the actual router.
    apply_to_router(
        router,
        interface,
        enabled,
    )

    print("\nOPERATION SUCCESSFUL")


if __name__ == "__main__":
    set_interface(
        router="r1",
        interface="eth1",
        enabled=True,
    )
