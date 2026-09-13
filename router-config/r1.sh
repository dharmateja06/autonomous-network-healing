#!/bin/bash

ip addr add 10.0.12.1/30 dev eth1
ip addr add 10.0.13.1/30 dev eth2

sysctl -w net.ipv4.ip_forward=1

ip route add 10.0.23.0/30 via 10.0.12.2
