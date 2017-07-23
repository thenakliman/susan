======================
Database Consideration
======================

Use case to be considered for database design

1. Populate database for each MAC address.
   It should be possible to assign pre deterined IP address to a machine.
   therefor binding for a machine has to to be possible.

   For example
   .. code::

     host passacaglia {
       hardware ethernet 0:0:c0:5d:bd:95;
       fixed-address 192.168.100.10
       filename "vmunix.passacaglia";
       server-name "toccata.fugue.com";
     }


2. Mulitple network to be served.
   It might be possible for a server to serve multiple networks at the same
   time. Machine should be able to grant IP address in all the networks, it is
   connected.

   For examle

   .. code::
 

                       172.17.0.0/16
                       ||
                       \/
                +--------------+
                |              |
   10.20.1.0/24 |              |
        ------> |              | <----- 10.10.1.0/24
                |              |
                +--------------+
                        ^
                        |
                        |
                       192.168.0.0/16

  .. code::

    subnet 204.254.239.0 netmask 255.255.255.224 {
      range 204.254.239.10 204.254.239.20;
      option broadcast-address 204.254.239.31;
      option routers prelude.fugue.com;
    }

    # The other subnet that shares this physical network
    subnet 204.254.239.32 netmask 255.255.255.224 {
      range dynamic-bootp 204.254.239.10 204.254.239.20;
      option broadcast-address 204.254.239.31;
      option routers snarg.fugue.com;
    }

    

3. Specify ranges of subnet to be serve.(Verify this use case is possible or not)
   It should be possible to server multiple blocks of IP from the same network
   has to be served. For example, we have 172.17.0.0/24 and someone wants to
   serve 172.17.10.0-172.17.10.254 IPs and 172.17.20.0-172.17.20.254 and would
   like to manage other IPs under scheme 1.


Possible Interactions
=====================

1. Get available IP address for a request.
2. Reserve the IP address
3. Commit IP address
4. Get the parameters for a Host
5. Get all the parameters for a host
6. Release IP address to the available Pool


Possible Database Schema
========================

Subnet
------

  Columns: (
      ID,
      Name,
      Network,
      Netmask,
      StartIP,
      EndIP,
      Gateway,
  }

  primary_key, ID
  +------+------+---------+---------+---------+-------+---------+
  | ID   | name | network | netmask | StartIP | EndIP | Gateway |
  +------+------+---------+---------+---------+-------+---------+
  |      |      |         |         |         |       |         |
  +------+------+---------+---------+---------+-------+---------+
  |      |      |         |         |         |       |         |
  +------+------+---------+---------+---------+-------+---------+

binded_ips
==========

  This table handles IPs to be bind for which MAC and IPs are supplied
  through some means to database.

  binded_ips = (
      ID,
      IP,
      MAC,
      subnet,
      Interface
  )

  unique_key: ID
  primary_key: IP, MAC, subnet.ID(foregin key), Interface

Parameters
==========

  Parameters: (
      subnet.ID,
      binded_ip.ID,
      1(or respecitve Name),
      2(or respective Name),
      3(or respective Name),
  )

  primary_key: subnet.ID, binded_ip.ID
  Foreign Key: subnet.ID, binded_ip.ID

  +--------------+-------+------+----------+
  |  subnet_id   |  1    |  2   | - - -  - |
  +--------------+-------+------+----------+
  |              |       |      |          |
  +--------------+-------+------+----------+
  |              |       |      |          |
  +--------------+-------+------+----------+


Reserved_ip
===========

  reserved_ip = (
      IP,
      MAC,
      subnet_id,
      Interface,
      Lease_time,
      renew_time,
      expire_time
  )

  primary_key: IP, MAc, subnet_id, Interface
  Foreign Key: subnet_id


========
Appendix
========

Following is sample configuration file for DHCP


.. code::

 # dhcpd.conf
 #
 # Sample configuration file for ISC dhcpd
 #

 # option definitions common to all supported networks...
 option domain-name "fugue.com";
 option domain-name-servers toccata.fugue.com;

 option subnet-mask 255.255.255.224;
 default-lease-time 600;
 max-lease-time 7200;

 subnet 204.254.239.0 netmask 255.255.255.224 {
   range 204.254.239.10 204.254.239.20;
   option broadcast-address 204.254.239.31;
   option routers prelude.fugue.com;
 }

 # The other subnet that shares this physical network
 subnet 204.254.239.32 netmask 255.255.255.224 {
   range dynamic-bootp 204.254.239.10 204.254.239.20;
   option broadcast-address 204.254.239.31;
   option routers snarg.fugue.com;
 }

 subnet 192.5.5.0 netmask 255.255.255.224 {
   range 192.5.5.26 192.5.5.30;
   option name-servers bb.home.vix.com, gw.home.vix.com;
   option domain-name "vix.com";
   option routers 192.5.5.1;
   option subnet-mask 255.255.255.224;
   option broadcast-address 192.5.5.31;
   default-lease-time 600;
   max-lease-time 7200;
 }

 # Hosts which require special configuration options can be listed in
 # host statements.   If no address is specified, the address will be
 # allocated dynamically (if possible), but the host-specific information
 # will still come from the host declaration.

 host passacaglia {
   hardware ethernet 0:0:c0:5d:bd:95;
   filename "vmunix.passacaglia";
   server-name "toccata.fugue.com";
 }

 # Fixed IP addresses can also be specified for hosts.   These addresses
 # should not also be listed as being available for dynamic assignment.
 # Hosts for which fixed IP addresses have been specified can boot using
 # BOOTP or DHCP.   Hosts for which no fixed address is specified can only
 # be booted with DHCP, unless there is an address range on the subnet
 # to which a BOOTP client is connected which has the dynamic-bootp flag
 # set.
 host fantasia {
   hardware ethernet 08:00:07:26:c0:a5;
   fixed-address fantasia.fugue.com;
 }

 # If a DHCP or BOOTP client is mobile and might be connected to a variety
 # of networks, more than one fixed address for that host can be specified.
 # Hosts can have fixed addresses on some networks, but receive dynamically
 # allocated address on other subnets; in order to support this, a host
 # declaration for that client must be given which does not have a fixed
 # address.   If a client should get different parameters depending on
 # what subnet it boots on, host declarations for each such network should
 # be given.   Finally, if a domain name is given for a host's fixed address
 # and that domain name evaluates to more than one address, the address
 # corresponding to the network to which the client is attached, if any,
 # will be assigned.
 host confusia {
   hardware ethernet 02:03:04:05:06:07;
   fixed-address confusia-1.fugue.com, confusia-2.fugue.com;
   filename "vmunix.confusia";
   server-name "toccata.fugue.com";
 }

 host confusia {
   hardware ethernet 02:03:04:05:06:07;
   fixed-address confusia-3.fugue.com;
   filename "vmunix.confusia";
   server-name "snarg.fugue.com";
 }

 host confusia {
   hardware ethernet 02:03:04:05:06:07;
   filename "vmunix.confusia";
   server-name "bb.home.vix.com";
 }


Following is the lease file being maintained

.. code::

 lease {
   interface "wlo1:avahi";
   fixed-address 192.168.4.110;
   option subnet-mask 255.255.255.0;
   option routers 192.168.4.1;
   option dhcp-lease-time 86400;
   option dhcp-message-type 5;
   option domain-name-servers 8.8.8.8,163.53.86.9;
   option dhcp-server-identifier 192.168.4.1;
   renew 5 2017/07/14 12:04:05;
   rebind 5 2017/07/14 22:55:29;
   expire 6 2017/07/15 01:55:29;
 }
 lease {
   interface "ns01";
   fixed-address 172.30.10.10;
   option subnet-mask 255.255.255.0;
   option routers 172.30.10.1;
   option dhcp-lease-time 10000;
   option dhcp-message-type 5;
   option domain-name-servers 8.8.8.8;
   renew 6 2017/07/22 16:36:49;
   rebind 6 2017/07/22 17:57:59;
   expire 6 2017/07/22 18:18:49;
 }
