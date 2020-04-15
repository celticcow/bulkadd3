Bulk Add 3

Checkpoint bulkadd for firewall hosts,networks, and service objects

example:
host,1.1.1.1,group11
host,2.2.2.2,group11
host,1.1.1.1,group21
network,1.0.1.0/24,group21
network,1.0.1.0/24,group99
network,1.0.1.0/24,group91
host,3.3.3.3,nogroup
host,3.3.2.3,nogroup
network,2.2.0.0/16,nogroup
network,2.2.2.0/24,nogroup
service,tcp,80
service,tcp,9999
service,tcp,8877
service,udp,9999
service,udp,8877

nogroup will not put the network or host in a group.

service objects will not put in a group.

Version 0.8:

bug list:


--------------------
Web Version:

bulk.html :
todo : 
	does network existing add to group ?
	test with more use cases
	promote up to prod

bulk.py :
	add in more test cases
	error checking
	output formatting
