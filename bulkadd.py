#!/usr/bin/python3 -W ignore::DeprecationWarning

import requests
import json
import sys
import csv
import time
import getpass
import ipaddress
import apifunctions

#remove the InsecureRequestWarning messages
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

"""
gregory.dunlap / celtic_cow
bulk add script.
take in csv file in format   (host/network),(ip/subnet+cidr),(group_name)
                             (service),(tcp/udp),(port num)
"""


def csvisgood(ifile):
    with open(ifile, newline='') as csvfile:
        csvreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in csvreader:
            row_type = row[0]
            row_data = row[1]
            row_grp  = row[2]            

            #if(debug == 1):
                #print(row_type, row_data, row_grp)
            try:
                if(rowisclean(row_type, row_data, row_grp)):
                    pass
                    #print("ROW IS CLEAN")
                else:
                    print("ROW IS INVALID")
                    print(row_type, row_data, row_grp)
                    return False
            except:
                print("ROW IS INVALID")
                print(row_type, row_data, row_grp)
                return False
    return True


def rowisclean(ctype, cdata, cgrp):
    if(ctype == "host"):
        if(ipaddress.ip_address(cdata)):
            pass
            #print("valid ip")
        else:
            return False
    elif(ctype == "network"):
        if(ipaddress.ip_network(cdata)):
            pass
            #print("valid network")
        else:
            return False
    elif(ctype == "service"):
        if((cdata == "tcp") or (cdata == "udp")):
            tmpnum = int(cgrp)
            if((tmpnum <= 65535) and (tmpnum >= 1)):
                pass
                #print("valid port")
            else:
                return False
        else:
            return False
    elif(ctype == "group"):
        pass
    else:
        print("things have gone sideways on your csv")
        return False
    return True

def main():
    
    debug = 1

    inputfile = sys.argv[1]
    
    print("CheckPoint BulkAdd3  version 0.85")

    #before we login to the mds ... make sure input file is good
    if(csvisgood(inputfile) == False):
        print("input CSV is malformed.")
        exit(1)

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

            addobj = 1

            if(debug ==1):
                print(row_type, row_data, row_grp)
            if(row_type == "service"):
                #data should be in format of (service,<tcp/udp>,<number>)
                if(row_data == "tcp"):
                    apifunctions.add_a_tcp_port(ip_addr,row_grp,sid)
                if(row_data == "udp"):
                    apifunctions.add_a_udp_port(ip_addr,row_grp,sid)
            elif(row_type == "group"):
                # row_data will have group, row_grp will have group we want to add into
                # add row_data group as a member to row_grp
                movefwd = 1
                if(apifunctions.group_exist(ip_addr, row_data, sid) == False):
                    print("Source Group does not exist. Do you want to create (yes/no). If you say No this line will be slipped ", row_data)
                    toadd = input("(yes/no) : ")
                    if(toadd == "yes"):
                        apifunctions.add_a_group(ip_addr, row_data, sid)
                    else:
                        movefwd = 0
                if(apifunctions.group_exist(ip_addr, row_grp, sid) == False):
                    print("Source Group does not exist. Do you want to create (yes/no). If you say No this line will be slipped ", row_grp)
                    toadd = input("(yes/no) : ")
                    if(toadd == "yes"):
                        apifunctions.add_a_group(ip_addr, row_grp, sid)
                    else:
                        movefwd = 0

                if(movefwd == 1):
                    #either both groups existed or we created both ... either way lets do this
                    apifunctions.add_group_to_group(ip_addr, row_data, row_grp, sid)
            # end elif group
            else:
                if(row_grp == "nogroup"):
                    ## we're not going to place this in a group
                    if(row_type == "network"):
                        tmp = row_data.split('/')
                        apifunctions.add_a_network(ip_addr, prefix+tmp[0], tmp[0], apifunctions.calcDottedNetmask(int(tmp[1])), sid)
                    if(row_type == "host"):
                        apifunctions.add_a_host(ip_addr, prefix+row_data, row_data, sid)
                else:
                    ## we doing some group stuff
                    if(apifunctions.group_exist(ip_addr, row_grp, sid) == False):
                        print("Group in row does not exist do you want to create (yes/no) if you say no this line will be skipped ", row_grp)
                        toadd = input("(yes / no) : ")
                        if(toadd == "yes"):
                            apifunctions.add_a_group(ip_addr, row_grp, sid)
                        else:
                            addobj = 0

                    if(addobj == 1):
                        #this is a valid group
                        if(row_type == "network"):
                            tmp = row_data.split('/')
                            apifunctions.add_a_network_with_group(ip_addr, prefix+tmp[0], tmp[0], apifunctions.calcDottedNetmask(int(tmp[1])), row_grp, sid)
                        if(row_type == "host"):
                            apifunctions.add_a_host_with_group(ip_addr, prefix+row_data, row_data, row_grp, sid)
                #end if(grp = nogroup)
            #end else --- network object
        #end for row in csvreader
    #end with open


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

if __name__ == "__main__":
    main()