from datetime import datetime
import uuid


def create_alarm(link, device, interface, fault_type, severity="CRITICAL"):
    alarm = {
        "alarm_id": f"ALM-{uuid.uuid4().hex[:8].upper()}",
        "timestamp": datetime.now().isoformat(),
        "link": link,
        "device": device,
        "interface": interface,
        "fault_type": fault_type,
        "severity": severity,
        "status": "ACTIVE",
    }

    return alarm


def print_alarm(alarm):
    print("\n========================================")
    print("             NETWORK ALARM")
    print("========================================")

    print(f"Alarm ID   : {alarm['alarm_id']}")
    print(f"Timestamp  : {alarm['timestamp']}")
    print(f"Link       : {alarm['link']}")
    print(f"Device     : {alarm['device']}")
    print(f"Interface  : {alarm['interface']}")
    print(f"Fault      : {alarm['fault_type']}")
    print(f"Severity   : {alarm['severity']}")
    print(f"Status     : {alarm['status']}")


if __name__ == "__main__":
    test_alarm = create_alarm(
        link="R1-R2",
        device="r1",
        interface="eth1",
        fault_type="INTERFACE_DOWN",
    )

    print_alarm(test_alarm)
