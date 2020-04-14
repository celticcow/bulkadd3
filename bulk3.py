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

def add_host(host, group, ip_addr, prefix, sid):
    if(group == "None"):
        apifunctions.add_a_host(ip_addr, prefix+host, host, sid)
    else:
        apifunctions.add_a_host_with_group(ip_addr, prefix+host, host, group,sid)

def add_network(net, mask, group, ip_addr, prefix, sid):
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
    cma_base = form.getvalue('dcma')

    #dcma_map = {
    #    'adm25' : '146.18.96.25',
    #    'adm26' : '146.18.96.26',
    #    'adm27' : '146.18.96.27'
    #}
    dcma_map = {
        'adm25' : {'cma' : '146.18.96.25', 'mds' : '146.18.96.16'},
        'adm26' : {'cma' : '146.18.96.26', 'mds' : '146.18.96.16'},
        'adm27' : {'cma' : '146.18.96.27', 'mds' : '146.18.96.16'},
    }
    #print(cma_map['adm27']['cma'])
    #print(cma_map['adm27']['mds'])

    mds_ip = dcma_map[cma_base]['mds']
    cma_ip = dcma_map[cma_base]['cma']

    ## html header and config data dump
    print ("Content-type:text/html\r\n\r\n")
    print ("<html>")
    print ("<head>")
    print ("<title>Bulk Add Results</title>")
    print ("</head>")
    print ("<body>")
    print("Bulk Add<br><br>")

    print(cma_ip + "<br>")

    print(dcma_map[cma_base])
    print("<br>")

    sid = apifunctions.login("gdunlap", "1qazxsw2", mds_ip, cma_ip)  

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

    time.sleep(5)

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
