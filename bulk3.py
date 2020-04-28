#!/usr/bin/python3 -W ignore::DeprecationWarning

import requests
import json
import sys
import time
import ipaddress
import apifunctions
import cgi,cgitb

#remove the InsecureRequestWarning messages
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

"""
Greg_Dunlap / CelticCow
"""

"""
convert a CIDR 24 to say 255.255.255.0
put here because dest server had old version of this.
"""
def calcDottedNetmask(mask):
    bits = 0
    for i in range(32-mask,32): 
        bits |= (1 << i)
    return "%d.%d.%d.%d" % ((bits & 0xff000000) >> 24, (bits & 0xff0000) >> 16, (bits & 0xff00) >> 8 , (bits & 0xff))

"""
prob move to apifunctions at later time
need to know object type of something where
name_exist() is true but is it a conflict or not
"""
def get_obj_type(ip_addr, name, sid):
    check_type = {"order" : [{"ASC" : "name"}], "in" : ["name", name] }
    chktype = apifunctions.api_call(ip_addr, "show-objects", check_type, sid)

    total = chktype['total']

    if(total > 1):
        return("multiple")
    elif(total == 0):
        return("zero")
    else:
        return(chktype['objects'][0]['type'])

    

def add_host(host, group, ip_addr, prefix, sid):
    print("In function add_host()<br>")
    
    if((apifunctions.name_exist(ip_addr, prefix+host, sid) == True) and (get_obj_type(ip_addr, prefix+host, sid) != "host")):
        print("<br>ISSUE HERE<br>")
        print("Object in use with same name that is not a host<br>")
    else:
        if(group == "None"):
            apifunctions.add_a_host(ip_addr, prefix+host, host, sid)
        else:
            apifunctions.add_a_host_with_group(ip_addr, prefix+host, host, group,sid)

def add_network(net, mask, group, ip_addr, prefix, sid):
    print("in function add_network()<br>")
    if(len(mask) < 3):
        # we have a cidr block
        tmp_mask = calcDottedNetmask(int(mask))
        mask = tmp_mask
    
    if((apifunctions.name_exist(ip_addr, prefix+net, sid) == True) and (get_obj_type(ip_addr, prefix+net, sid) != "network")):
        print("<br>Issue Found")
        print("Object in use with same name that is not a network<br>")
    else:
        if(group == "None"):
            apifunctions.add_a_network(ip_addr, prefix+net, net, mask, sid)
        else:
            apifunctions.add_a_network_with_group(ip_addr, prefix+net, net, mask, group, sid)


"""
determine if object is host or network and is valid
"""
def what_am_i(obj):
    debug = 1

    parts = obj.split('/')
    mylen = len(parts)

    if(mylen == 2):
        #Network Part
        print("len = 2<br>")
        try:
            if(ipaddress.ip_network(obj)):
                print("valid network<br>")
                return("network")
            else:
                print("invalid network<br>")
                return("invalid")
        except ValueError:
            print("Not a valid network")
            return("invalid")
    elif(mylen == 1):
        #Host Part
        print("len = 1<br>")
        try:
            if(ipaddress.ip_address(parts[0])):
                print("valid ip<br>")
                return("host")
            else:
                print("Invalid HOST<br>")
                return("invalid")
        except ValueError:
            print("Not a valid IP")
            return("invalid")
    else:
        print("um ... dude")
        return("invalid")
#end of what_am_i
    

def main():
    debug = 1

    #create instance of field storage
    form = cgi.FieldStorage()
    cma_base = form.getvalue('cma')   #modified for test
    userid = form.getvalue('user')
    passwd = form.getvalue('password')

   
    cma_map = {
        'adm1'  : {'cma' : '192.168.159.151', 'mds' : '192.168.159.150'},
        'adm2'  : {'cma' : '204.135.121.152', 'mds' : '204.135.121.150'},
        'adm3'  : {'cma' : '204.135.121.153', 'mds' : '204.135.121.150'},
        'adm5'  : {'cma' : '192.168.159.155', 'mds' : '192.168.159.150'},
        'adm6'  : {'cma' : '204.135.121.156', 'mds' : '204.135.121.150'},
        'adm7'  : {'cma' : '204.135.121.157', 'mds' : '204.135.121.150'},
        'adm8'  : {'cma' : '204.135.121.158', 'mds' : '204.135.121.150'},
        'adm10' : {'cma' : '192.168.159.160', 'mds' : '192.168.159.150'},
        'adm11' : {'cma' : '192.168.159.161', 'mds' : '192.168.159.150'},
        'adm12' : {'cma' : '192.168.159.162', 'mds' : '192.168.159.150'},
        'adm13' : {'cma' : '192.168.159.163', 'mds' : '192.168.159.150'},
        'adm14' : {'cma' : '204.135.121.164', 'mds' : '204.135.121.150'},
        'adm17' : {'cma' : '192.168.159.167', 'mds' : '192.168.159.150'},
        'adm19' : {'cma' : '192.168.159.169', 'mds' : '192.168.159.150'},
        'adm24' : {'cma' : '204.135.121.174', 'mds' : '204.135.121.150'},
    }

    dcma_map = {
        'adm25' : {'cma' : '146.18.96.25', 'mds' : '146.18.96.16'},
        'adm26' : {'cma' : '146.18.96.26', 'mds' : '146.18.96.16'},
        'adm27' : {'cma' : '146.18.96.27', 'mds' : '146.18.96.16'},
    }

    mds_ip = cma_map[cma_base]['mds'] # mod to d
    cma_ip = cma_map[cma_base]['cma'] # mod to d

    ## html header and config data dump
    print ("Content-type:text/html\r\n\r\n")
    print ("<html>")
    print ("<head>")
    print ("<title>Bulk Add Results</title>")
    print ("</head>")
    print ("<body>")
    print("Bulk Add<br><br>")

    print(cma_ip + "<br>")

    print(cma_map[cma_base]) # mod to d
    print("<br>")

    sid = apifunctions.login(userid, passwd, mds_ip, cma_ip)  

    if(debug == 1):
        print("session id : " + sid + "<br>")
    
    group_to_use     = form.getvalue('group')
    objects_raw      = form.getvalue('objects')
    prefix           = form.getvalue('prefix')

    objects_s1 = str(objects_raw) # odd i know but ya got to
    objects_s2 = objects_s1.split(' ')
    objects_s3 = objects_s2[0].split()

    #if(debug == 1):
    #    print("Group to add to<br>")
    #    print("-" + group_to_use + "-")
    #    print("<br>")

    
    if(group_to_use == None):
        print("no group to add<br>")
    else:
        #if something with the proposed group name exist.  tell user (IN CAPS) and still create objects
        if(apifunctions.name_exist(mds_ip, group_to_use, sid) == True):
            #
            # issue here .. if it exist but is a group ?
            #
            if(get_obj_type(mds_ip, group_to_use,sid) != "group"):
                print("CAN'T ADD GROUP <br>OBJECT WITH THIS NAME ALREADY EXIST<br>MOVING FORWARD WITHOUT GROUP<br>")
                group_to_use = None
        else:
            apifunctions.add_a_group(mds_ip, group_to_use, sid)
    #if(group_to_use == "None"):
    #    print("no group to add <br>")
    #else:
    #    apifunctions.add_a_group(mds_ip, group_to_use, sid)

    print("<br>")
    print("Object Listing<br>")
    for obj in objects_s3:
        print(obj)
        print("<br>")
        obj_type = what_am_i(obj)
        print("*****<br>")
        print(obj_type)
        print("<br>")
        print("-----<br>")

        if(obj_type == "host"):
            add_host(obj, group_to_use, mds_ip, prefix, sid) 
        if(obj_type == "network"):
            parts = obj.split('/')
            add_network(parts[0], parts[1], group_to_use, mds_ip, prefix, sid) 

        #print(objects_raw)

    print("<br>Start of Publish ... zzzzzz")
    time.sleep(5)
    publish_result = apifunctions.api_call(mds_ip, "publish", {}, sid)
    print("publish results : " + json.dumps(publish_result))

    time.sleep(20)

    ### logout
    logout_result = apifunctions.api_call(mds_ip, "logout", {}, sid)
    if(debug == 1):
        print(logout_result)
    print("------- end of program -------")
    print("<br><br>")
    print("</body>")
    print("</html>")
#end of main()

if __name__ == "__main__":
    main()
