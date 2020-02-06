#!/usr/bin/python3 -W ignore::DeprecationWarning

import requests
import json
import sys
import csv
import time
import getpass
import apifunctions

#remove the InsecureRequestWarning messages
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

"""
"""

if __name__ == "__main__":
    
    debug = 1

    inputfile = sys.argv[1]

    ip_addr = input("enter IP of MDS : ")
    ip_cma  = input("enter IP of CMA : ")
    user    = input("enter P1 user id : ")
    password = getpass.getpass('Enter P1 Password : ')

    prefix = input("Object Prefix : ")

    sid = apifunctions.login(user, password, ip_addr, ip_cma)

    if(debug == 1):
        print("session id : " + sid)

    with open(inputfile, newline='') as csvfile:
        csvreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in csvreader:
            row_type = row[0]
            row_data = row[1]
            row_grp  = row[2]

            if(debug ==1):
                print(row_type, row_data, row_grp)

            if(row_type == "network"):
                tmp = row_data.split('/')
                apifunctions.add_a_network_with_group(ip_addr, prefix+tmp[0], tmp[0], apifunctions.calcDottedNetmask(int(tmp[1])), row_grp, sid)
            if(row_type == "host"):
                apifunctions.add_a_host_with_group(ip_addr, prefix+row_data, row_data, row_grp, sid)

    ### some times publish doesn't work and sits in dashboard

    ### publish
    print("Start of Publish ... zzzzzz")
    time.sleep(20)
    publish_result = apifunctions.api_call(ip_addr, "publish", {}, sid)
    print("publish results : " + json.dumps(publish_result))

    time.sleep(20)

    ### logout
    logout_result = apifunctions.api_call(ip_addr, "logout", {}, sid)
    if(debug == 1):
        print(logout_result)
#endof main()