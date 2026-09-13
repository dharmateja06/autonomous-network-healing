# Autonomous Network Healing Platform

## Project Overview

The Autonomous Network Healing Platform is a Network Management System (NMS)
that detects network failures, identifies their root cause, and automatically
restores failed network interfaces.

The system follows an autonomous healing pipeline:

Network Failure
      ↓
Network Monitoring
      ↓
Alarm Generation
      ↓
Kafka Event Transport
      ↓
Root Cause Analysis (RCA)
      ↓
NETCONF Configuration
      ↓
Automatic Interface Restoration
      ↓
Connectivity Verification
      ↓
Recovery

## Problem Statement

Manual intervention during network failures can increase recovery time and
network downtime.

This project implements an autonomous mechanism that detects interface
failures, identifies the affected interface, applies a corrective
configuration automatically, and verifies that network connectivity has
been restored.

## Architecture

The platform consists of the following components:

1. Network Topology
   - Three routers: R1, R2, and R3
   - Containerlab-based topology
   - Linux containers configured as routers

2. Network Monitoring
   - Continuously monitors network links
   - Detects UP → DOWN transitions
   - Generates network alarms

3. Alarm Management
   - Creates structured alarms
   - Includes alarm ID, timestamp, device, interface, fault type, severity,
     and status

4. Kafka / Redpanda
   - Transports network alarms asynchronously
   - Topic: network-alarms

5. Root Cause Analysis
   - Examines router interface operational states
   - Identifies interface failures

6. NETCONF / YANG
   - Uses NETCONF for configuration operations
   - Uses a custom YANG model for interface configuration
   - NETCONF server implemented using netopeer2/sysrepo

7. Autonomous Healing
   - Restores failed interfaces
   - Supports up to three healing attempts
   - Verifies actual interface state
   - Verifies network connectivity

8. NMS Status View
   - Displays current network link status
   - Displays router status
   - Displays recent healing events

## Technologies Used

- Ubuntu Linux
- Python
- Docker
- Containerlab
- Kafka / Redpanda
- NETCONF
- YANG
- Sysrepo
- Netopeer2
- ncclient
- Linux networking
- Static routing

## Network Topology

R1 -------- R2
 |          |
 |          |
 +----------+
      R3

Links:

R1-R2
R1-R3
R2-R3

## Healing Workflow

When a link failure occurs:

1. The monitoring system detects the link going DOWN.
2. A critical network alarm is generated.
3. The alarm is published to Kafka.
4. The RCA engine receives the alarm.
5. RCA checks the affected router interfaces.
6. The root cause is identified.
7. The healing engine starts.
8. NETCONF configuration is applied.
9. The actual Linux router interface is restored.
10. Interface state is verified.
11. Connectivity is verified using ping.
12. The healing operation is marked successful.
13. The event is stored in the healing log.

## Fault Injection

A network failure can be simulated using:

docker exec clab-anh-r1 ip link set eth1 down

The monitoring system automatically detects the failure and starts the
healing workflow.

## Healing Verification

The system verifies:

- Interface operational state
- Router configuration
- Network connectivity
- Healing result

Example successful result:

R1-R2: Interface restored.
R1-R2: CONNECTIVITY VERIFIED
R1-R2: HEALING SUCCESSFUL

## Retry Mechanism

The healing engine supports up to three attempts.

If the first attempt fails, the system waits and retries automatically.

After all attempts fail, the event is recorded as:

result=FAILED

## Logging

Healing events are stored in:

logs/healing.log

Example:

2026-09-13T22:40:35.595048 | link=R1-R2 | router=r1 | interface=eth1 | attempt=1 | result=SUCCESS

## NMS Dashboard

The NMS status view displays:

- Network link status
- Router status
- Recent healing events

Run:

python nms_dashboard.py

## Final Result

The system successfully demonstrates autonomous network healing:

Fault Detection
→ Alarm
→ Kafka
→ RCA
→ NETCONF
→ Automatic Healing
→ Connectivity Verification
→ Recovery

The final validation successfully recovered the R1-R2 link automatically
after fault injection.

## Project Outcome

The platform demonstrates how an NMS can reduce dependence on manual
intervention by automatically detecting, diagnosing, repairing, and
verifying network failures.
