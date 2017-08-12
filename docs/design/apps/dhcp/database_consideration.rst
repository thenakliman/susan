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
      ID PRIMARY KEY,
      Name,
      Network,
      cidr,
      Gateway,
  )

  
  primary_key, ID
  +------+------+---------+---------+
  | ID   | name | network | cidr    |
  +------+------+---------+---------+
  |      |      |         |         |
  +------+------+---------+---------+
  |      |      |         |         |
  +------+------+---------+---------+

  NOTE: Multiple range within a subnet can be supported with non overlapping start
        and end IP address. How to choose primary key.

Range
=====

  columns: (
      ID PRIMARY KEY,
      subnet.ID FOREIGN KEY,
      StartIP,
      EndIP,
  )

  Primary Key: ID
  Foreign Key: ID (Subnet.id)

  NOTE: This table has been introduced to make sure that multiple ranges can
        exist with subnet.

Parameters
==========


Approach 1:


  Parameters: (
      subnet.ID PRIMARY KEY FOREIGN KEY,
      binded_ip.ID PRIMARY KEY FOREIGN KEY,
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


  NOTE: Subnet and binded_ip.ID has been provide to make sure that host
        parameters can be fetched based on subnet and IP binded_ip. If
        host parameter is fetched based on binded IP then that IP must
        be part of subnet.

  It will require table to normalize because some of the paramers can
  be list, for example list of nameserver, routers etc. So we might
  have to create more tables to avoid redundancy and consistency issues
  in the database.


Approach 2:

  Parameters: (
      subnet.ID FOREIGN KEY,
      binded_ip.ID FOREIGN KEY,
      data(type pickle) # use dict
  )

  Of course, it will increase some processing power by pickle and unpickle.
  It seems worthy to use, it avoids to create un neccessary tables and
  does not make maintenance diffcult. However the maintenence cost is
  going to be negligble with both the approaches because protocols rarely
  changes or they just get expented and stay backward compatible. Protocol
  change seems to be rare at this point, it is better to move with second
  one.
  
Reserved_ip
===========
  Purpose of this table is to maintain binded ips and reserved ips by
  the dhcp server.

  reserved_ip = (
      IP,
      MAC,
      subnet_id,
      state,
      is_reserved,
      Interface,
      Lease_time,
      renew_time,
      expire_time
  )

  primary_key: IP, MAc, subnet_id, Interface
  Foreign Key: subnet_id


  is_reserved: maintains whether a particular ip address is reserved or not.
               keeping "state" and its value can be, 'reserved', 'expired' and
              'binded', it will introduce the problem of state transition, for
               expample::

                             +--------------+         +-----------+  +---------+
                             | Unallocated: |         |   binded  |<-|reserved |
                             | assign an IP | ---->   +-----------+  +---------+
                             |  from range  |               |             |
                             +--------------+               |             |
                                    ^                       \/            |
                                    |                 +-----------+       |
                                    |                 |  expired  |       |
                                    |                 +-----------+       |
                                    |                       |             |
                                    +-----------------------+-------------+
                                          Y                       X

              On What bassis, decision should be made, whether it go to X or Y.
              Once an IP address is expired then it's state changes from
              expired to reserved or delete that entry from the table. How do
              we make decision for this.

              So if two approaches can be,

              Approach 1: Make one more table and just keep the IP address of
                          reserved once. Once that we have to move then we can
                          check whether it is reserved or not and we won't have
                          to make decision, whether go to reserved state or
                          unallocated. We can safely delete from binded table
                          be sure reserved once already exist in table and next
                          time makes decision.

              Approach 2: We just keep one column, is_reserved a bool variable.
                          Now, if an ip address is reserved then
                          this must be true. So if IP expire then we don't
                          to do anything because this entry is never to be
                          conflicted with any other MAC address or to be given
                          to anyone or so no need move to unallocated pool.
                          If this entry is false then delete it, even if ever
                          needed then expiry time is always there to identify
                          the "expiry" state. So deleted entry goes to
                          unallocated pool.

             NOTE: To improve and make it better approach 2, let's use state as
                   well to cleanly find out and expiry state and commit IPs.
                   After offer this IP does not have to be given to a other
                   nodes.

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
