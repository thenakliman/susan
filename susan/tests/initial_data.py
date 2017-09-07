import uuid

from susan.db.rdbms import datapath
from susan.db.rdbms import dhcp
from susan.db.rdbms import port


REQ_MAC = 'be:7e:55:53:31:d7'
OLD_MAC = '8a:89:1f:db:38:7c'
#OLD_MAC = REQ_MAC
DATAPATH = '117035352915020'
SUBNET_ID = '4e2dfe6e-9322-11e7-98b7-ace010fc1f0e'
NETWORK = '172.30.10.0'
GATEWAY = '172.30.10.1'
IP = '172.30.10.173'
BR_MAC = '6a:71:6a:a2:fc:4c'
START_IP = '172.30.10.200'
END_IP = '172.30.10.249'

#dhcp.DHCPDB().create_subnet(network=NETWORK, cidr=24, gateway=GATEWAY, server=GATEWAY, next_server=GATEWAY)
#datapath.Datapath().add_datapath(id_=DATAPATH, host=GATEWAY, port=55140)
#port.Port().delete_port(datapath_id=DATAPATH, subnet_id=SUBNET_ID)
#port.Port().add_port(datapath_id=DATAPATH, port=1, mac=REQ_MAC, subnet_id=SUBNET_ID)
#port.Port().add_port(datapath_id=DATAPATH, port=2, mac=None, subnet_id=SUBNET_ID)
#port.Port().add_port(datapath_id=DATAPATH, port=3, mac=None, subnet_id=SUBNET_ID)
#dhcp.DHCPDB().delete_reserved_ip(mac=OLD_MAC, subnet_id=SUBNET_ID)
#dhcp.DHCPDB().add_reserved_ip(mac=REQ_MAC, ip=IP, is_reserved=1, subnet_id=SUBNET_ID)
#dhcp.DHCPDB().add_reserved_ip(mac=BR_MAC, ip=GATEWAY, is_reserved=1, subnet_id=SUBNET_ID)
#dhcp.DHCPDB().create_range(subnet_id=SUBNET_ID, start_ip=START_IP, end_ip=END_IP)

data = {
    1: '255.255.255.0',
    3: GATEWAY 
}

#dhcp.DHCPDB().add_parameter(mac=REQ_MAC, subnet_id=SUBNET_ID, data = data)
dhcp.DHCPDB().add_parameter(mac=None, subnet_id=SUBNET_ID, data = data)
