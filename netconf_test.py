from ncclient import manager


HOST = "127.0.0.1"
PORT = 830
USERNAME = "netconf"
PASSWORD = "teja"

config = """
<config xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">
  <interfaces xmlns="urn:anh:router">
    <interface>
      <name>eth1</name>
      <enabled>true</enabled>
      <description>Primary R1-R2 link</description>
    </interface>
  </interfaces>
</config>
"""

print("Connecting to NETCONF server...")

with manager.connect(
    host=HOST,
    port=PORT,
    username=USERNAME,
    password=PASSWORD,
    hostkey_verify=False,
    allow_agent=False,
    look_for_keys=False,
    timeout=10,
) as m:

    print("NETCONF CONNECTION SUCCESSFUL")
    print("\nSending configuration using NETCONF edit-config...")

    reply = m.edit_config(
        target="running",
        config=config,
    )

    print("\nNETCONF CONFIGURATION APPLIED")
    print(reply.xml)
