#!/bin/sh
set -eu
# This container owns only its network namespace; jobs have no NET_ADMIN.
iptables -P OUTPUT DROP
iptables -P INPUT DROP
iptables -P FORWARD DROP
ip6tables -P OUTPUT DROP
ip6tables -P INPUT DROP
ip6tables -P FORWARD DROP
iptables -A INPUT -i lo -j ACCEPT
iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
iptables -A OUTPUT -o lo -j ACCEPT
# Deny special-use destinations before accepting established Internet traffic.
for subnet in 0.0.0.0/8 10.0.0.0/8 100.64.0.0/10 127.0.0.0/8 169.254.0.0/16 172.16.0.0/12 192.0.0.0/24 192.0.2.0/24 192.168.0.0/16 198.18.0.0/15 198.51.100.0/24 203.0.113.0/24 224.0.0.0/4 240.0.0.0/4; do
  iptables -A OUTPUT -d "$subnet" -j REJECT
done
for address in $HOST_ADDRESSES; do
  iptables -A OUTPUT -d "$address" -j REJECT
done
iptables -A OUTPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT
iptables -A OUTPUT -d 1.1.1.1 -p udp --dport 53 -j ACCEPT
iptables -A OUTPUT -d 1.1.1.1 -p tcp --dport 53 -j ACCEPT
iptables -A OUTPUT -p tcp -m multiport --dports 80,443 -j ACCEPT
# A ready marker is created only after every rule succeeds.
touch /tmp/ready
exec sleep infinity
