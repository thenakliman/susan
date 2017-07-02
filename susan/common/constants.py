import enum

# =============================================
# Common Constants
# =============================================
ZERO_IPADDR = '0.0.0.0'
BROADCAST_IP = '255.255.255.255'
BROADCAST_MAC = 'ff:ff:ff:ff:ff:ff'

# =============================================
# DHCP constants
# =============================================

class DHCP(object):
    CLIENT_PORT=68
    SERVER_PORT=67
