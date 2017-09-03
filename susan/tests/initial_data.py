import uuid

from susan.db.rdbms import datapath
from susan.db.rdbms import dhcp
from susan.db.rdbms import port


#dhcp.DHCPDB().create_subnet(network='172.30.10.0', cidr=24, gateway='172.30.10.1', server='172.30.10.1', next_server='172.30.10.1')
#datapath.Datapath().add_datapath(id_='117035352915020', host='172.30.10.1', port=55140)
#port.Port().add_port(datapath_id='117035352915020', port=1, mac='8a:89:1f:db:38:7c', subnet_id='4c5c88c2-9074-11e7-9761-ace010fc1f0e')
#dhcp.DHCPDB().add_reserved_ip(mac='8a:89:1f:db:38:7c', ip='172.30.10.57', is_reserved=1, subnet_id='4c5c88c2-9074-11e7-9761-ace010fc1f0e')
#dhcp.DHCPDB().add_reserved_ip(mac='6a:71:6a:a2:fc:4c', ip='172.30.10.1', is_reserved=1, subnet_id='4c5c88c2-9074-11e7-9761-ace010fc1f0e')

data = {
    1: '255.255.255.0',
    3: '172.30.10.1'
}

dhcp.DHCPDB().add_parameter(mac='8a:89:1f:db:38:7c', subnet_id='4c5c88c2-9074-11e7-9761-ace010fc1f0e', data = data)
