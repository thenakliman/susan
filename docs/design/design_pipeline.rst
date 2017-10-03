++++++++++++++++
Pipleline design
++++++++++++++++

susan uses yaml file to design pipleline. A pipleine is basically a acyclic
directed graph, where a node represent tables and edge represent a goto action.
Each table has a number. All the flows start from a single table number 0. For
example


.. code::
    ::
                        +----------+
                        | table 0  |
                        +----------+
                             |
            +----------------+-------------+---------------+
            |                |             |               |
        +---+-----+     +----+----+   +----+----+     +----+----+
        | table 1 |     | table 2 |   | table 3 |     | table 4 |
        +---------+     +----+----+   +----+----+     +----+----+
            |                |             |               |
            |                |             |               |
            |                |             |               |
            +-------+--------+             |               |
                    |                      |               |
               +----+----+                 |    +----------+
               | table 5 |                 |    |          |
               +----+----+                 |    |          |
                    |                      |    |     +----+----+
                    +----------+-----------+    |     | table 6 |
                    |          |           |    |     +---------+
                    |     +----+----+      |    |
                    |     | table 7 |      |    |
                    |     +----+----+      |    |
                    |          |           |    |
                    +----------+-----------+----+
                                           |
                                     +-----+-----+
                                     | table 10  |
                                     +-----------+

  NOTE:: Arrow points downward in the diagram.


We have chains with following rules

1. They have one root node, where everything start. It is table number 0.
2. A table might go to multiple tables, but they can never go to the table
   having lower table number than its own.
3. There can be multiple nodes with degree one.
4. In the above diagram, we have table 6 and table 10, which does not have
   line originating from. They works as terminating point.
5. All the tables can terminate the further chains.


Each table is assigned some repsonibility, initially idea is to use only
one table per apps. All the apps are described using yaml,

For example, following pipeline has to be defined

.. code::
  ::

           +----------+
           | susan(0) |
           +---+------+
               ||                +----------+
               \/                | VLAN(12) |
      +--------+-------+------->>+ -------- |
      ||               ||        +----------+
      \/               \/
   +--+------+     +---+------+
   | L2(13)  |     | DNAT(15) |
   | -----   |     |          |
   +--+------+     +--+-------+
      |               |
      +----------->>+-+
      ||            ||
      \/            \/
   +--+------+   +--+-----+
   | ARP(16) |   | L3(17) |
   | ------  |   | -----  |
   +---------+   +--------+

   -----  -> Terminating App


.. code::

  susan:
    table: 0
    terminates: false
    config:
       key1: value1
       key2: value2
       key3: value3
       -
       -
    goto:
      - L2
      - DNAT
      - VLAN
  L2:
    table: 13
    terminates: true
    config:
      key1: value1
      key2: value2
      key3: value3
      -
      -
   goto:
      - ARP
      - L3
  L3:
    table: 17
    terminates: true
    config:
        key1: value1
        -
        -
  VLAN:
    table: 12
    terminates: true
    config:
        key1: value1
        -
        -
  DNAT:
    table: 15
    terminates: false
    config:
      key1: value1
      key2: value2
      -
    goto:
      - l3
  ARP:
    table: 16
    terminates: true
    config:
      key1: value1
      key2: value2
      -


Arrow has been used to indicate flow. \/ arrows for downward and >>, << for
right and left flow. there can not upward flow because a table can not have
goto statement having less than it's own table number.

---------------
Implementation:
---------------

There are multiple aspects and decision to be made let's start one by one

#. As explained earlier, the purpose of each table is to do one thing and our
   application is planned(can be changed later, if not possible) to use only
   one table to fullfill its purpose. But Goto action is used to move
   processing from one table to other therefore app code will have to use
   other table number. In a way we are referring them and dealing with
   multiple table, so one of the following approach can be used

       1. Define a base class for application to force applications, to
          implement a method **add_gotos** (name can be modified), which
          will be adding all Goto actions for a application. So this way,
          complexity of an application coupled closely with the application
          introducing it.

       2. Define a separate class, and which adds all the Goto actions for
          all the appilcations. This way, we are making all the application
          to deal with only and only with its own table. And a separate code
          adds all the Goto statement. So debugging related with Goto will
          be staying to that class only. Because we are having table number
          in yaml configuration files, therefore we know, where to add
          Goto actions.

   We have to deal with if's of an application related things therefore it will
   be a bad idea to move application related logic away from an application.
   Therefore approach **1** take toll over approach **2**. Approach **1** is
   recommended

   We are going to define a base class for applications

   .. code:: python

       class BaseApp(object):
           def __init__(self, *args, **kwargs):
               pass

           def add_gotos(self):
               pass

    Arguments can be decided later, while implementing but this class will make
    sure that applications have **add_gotos** methods to handle all the
    banches.

#. Table number's are provided in yaml file, therefore it makes the application
   highly configuration on demand. There are two approaches for selection of
   table numbers.

     1. Program automatically select table numbers and put them into database
        on their first run, may be during migrations. But the problem is, we
        can not reconfigure it easily, however it is possible but won't be
        possible much. And of course, we can not include in the decision
        making and can not make decision related to future related anticipated
        changes. Because if table number's are too close one after the other
        then adding a new table in between is impossible. We will have to
        move flows and shift them. It makes it difficult to reconfigure for
        and desinging of the pipeline.

     2. Users add table number through yaml file, which makes us to decide
        the pipeline and reconfigure and participate in design pipeline. It is
        always better approach and recommended.

   Above two approaches can be implemented or one can be implemented. However,
   i would like to make it the most configurable piece of software, so i will
   make it configurable and pluggable. So, anyone can implement, it's own way
   to make design pipeline, however in my opinion **first** one is enough, but
   making it configurable won't hurt. Approach **two** is one of the good
   algorithmic problem to implement, i would like to solve this problem.

.. code::
  ::

  + - - - - - - - - - - - - - - - - - - - - - -  -+
      Only One way of Pipeline Input to be used
  |                                               |
    +------+    +-------+            +-------+
  | |  Pi1 |    |  Pi2  |   -------- |  PiN  |    |
    +--+---+    +---+---+            +---+---+
  |    |            |                    |        |
  + - -| - - - - -  | - - - - -  - - - - | - - - -+
   ----+------------+--++----------------+------
                       ||
   ---++------++-------++--------------++-------
      ||      ||                       ||
    +-++-+  +-++-+                   +-++-+
    | C1 |  | C2 | - - - - - - - - - | CN |
    +----+  +----+                   +----+

    PiK --> Pi th type of pipeline input method
    Ci --> Connection point(Explained Later)

#. Before initializing of the susan, graph needs to be traversed and
   identified that it does not contain cycle.

#. Configurations can be any key value pair that might be needed by the
   application dynamically.

#. **terminates** options in yaml file, identifies that this application or
   table will act as the last table or application.

#. Customization of gotos can be done following ways

       1. User inherits from apps defined in susan and implements it's own
          **add_gotos** method, this way user is capable of handling the
          packet.

       2. User can pass gotos methods at the initialization of the script,
          and that method is assigned to **add_gotos** method of the class.

    Above mentions methods achieve the same things but different ways.
    Recommended way is, first one, because user might also want to customize
    some other methods as well. Second methods, leave developer with less
    options to change behaviour of class. So what, we are going to achieve
    through this framework is following

    .. code::


           +------+   +------+  +------+  +------+             +------+
           |      |   |      |  |      |  |      |             |      |
           |App 1 |   |App 2 |  |App 3 |  |App 4 |             |App N |
           |      |   |      |  |      |  |      | - - - - -   |      |
           |      |   |      |  |      |  |      |             |      |
           +--+---+   +--+---+  +--+---+  +--+---+             +--+---+
              |          |         |         |                    |
              |          |         |         |                    |
             ++-+       ++-+      ++-+      ++-+                 ++-+
             |C1|       |C2|      |C3|      |C4| - - - - - - -   |CN|
             ++++       ++++      ++++      ++++                 ++++
              ||         ||        ||        ||                   ||
              ||         ||        ||        ||                   ||
           ---++---------++--------++--------++-------------------++- Ps
           ---++---------++--------++--------++-------------------++-


            App i -> i th App
            Ci ->  i th Connection point


    Here **App i** is the susan application and **C i** is the i th connection
    point or **add_gotos**. These **add_gotos** are to be provided by
    inheritance therefore, this is the class inheriting the susan application.
     **Ps** represents the paths, which are configured by the
    connections(Ci). So wiring among the applications has to be customized by
    the user specified classes. This way user can control the design of the
    pipeline.

    From implementation perspective **App i** is the susan class implementing
    application and **C i** is the classe provided by the user of the
    application.

#.  User can provide default parameter for the applications through yaml file,
    parameters like, default DHCP release time etc.

#. After connecting all the things our structure of the application gets
   following

.. code::

      ::
                               +----+ +----+         +----+        |   +-----+
                               | A1 | | A2 |  ----   | AN |        +---+ Pi1 |
                               +-++-+ +-++-+         +-++-+        |   +-----+
        +-------+    ||          ||     ||             ||          |           
        |  DB1  +----+|        +-++-+ +-++-+         +-++-+        |   +-----+
        +-------+    ||        | C1 | | C2 |  ----   | CN |        +---+ Pi2 |
                     ||        +-++-+ +-++-+         +-++-+        |   +-----+
                     ||          || |   || |           || |        |    
                     ||       ---||-+---||-+-----------||-+--------+   
                     ||          ||     ||             ||          |    
        +-------+    ||      ----++-----++-------------++------    |           
        |  DB2  +----+|          ||     ||             ||          |   +-----+
        +-------+    ||          ||     ||    ----     ||          +---+ PiN |
                     ||          ||     ||             ||          |   +-----+
                     |+----------++-----++-------------++----
                     |+----------++-----++-------------++----
                     ||
                     ||
        +-------+    ||
        |  DBN  +----+|
        +-------+    ||


    Above diagram explains, how different components of apps will be stitched
    together and provide interface for almost everything and make it possible
    to provide customized behaviour
