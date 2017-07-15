"""Constants specific to dhcp app"""
# =============================================
# DHCP constants
# =============================================
# pylint: disable=too-few-public-methods
class DHCPPort(object):
    """Port information of DHCP"""
    CLIENT_PORT = 68
    SERVER_PORT = 67


class DHCPRequest(object):
    """Defined type of requests to mapping name for DHCP protocol messages
    """
    DHCPDISCOVER = 'discover'
    DHCPOFFER = 'offer'
    DHCPREQUEST = 'request'
    DHCPACK = 'ack'
    DHCPNACK = 'nack'
    DHCPDECLINE = 'decline'
    DHCPRELEASE = 'release'
    DHCPINFORM = 'inform'
