Attached is an example of Infiniband network topology discovery tool output file.

You should write a program in Python, or any other programming language of your choice - topo_parser, that parses this file, finds, and prints all connections in the network. The utility should be run as following:
topo_parser –h
print usage and exit
topo_parser –f topofile.topo
parse topofile.topo
topo_parser –p
print parsed topology
Infiniband network can be quite large (hundreds of thousands of network devices), as a result, the topology file can be large as well. Reading and parsing such file can take a while. Please propose an improved topo_parser version that allows the user to print existing topology while topo_parser is processing new topofile. Parsing progress should be reported to the user.
Infiniband network topology file explanation:

There are two types of devices – Switch and host.

Print the devices in order of connectivity:

For example:

Hosts

Switches

Switches

Hosts

 

Host:

sysimgguid=0xe41d2d03005cf34c

Port_id:= e41d2d03005cf34c

Connected to switch: switchguid=0x2c903007b78b0(2c903007b78b0), port=3

 

Pay attention that:

-          there can be more than one connection between devices.

-          There can be more than one port on host.