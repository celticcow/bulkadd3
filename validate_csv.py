#!/usr/bin/python3

import csv
import sys
import ipaddress

"""
test code to iron out csv validation
stand alone csv validation.
functions were copied into the bulk script
"""
def csvisgood(ifile):

    with open(ifile, newline='') as csvfile:
        csvreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in csvreader:
            row_type = row[0]
            row_data = row[1]
            row_grp  = row[2]            

            if(debug ==1):
                print(row_type, row_data, row_grp)
            try:
                if(rowisclean(row_type, row_data, row_grp)):
                    print("ROW IS CLEAN")
                else:
                    print("ROW IS INVALID")
                    return False
            except:
                print("ROW IS INVALID")
                return False
    return True


def rowisclean(ctype, cdata, cgrp):
    if(ctype == "host"):
        if(ipaddress.ip_address(cdata)):
                print("valid ip")
        else:
            return False
    elif(ctype == "network"):
        if(ipaddress.ip_network(cdata)):
            print("valid network")
        else:
            return False
    elif(ctype == "service"):
        if((cdata == "tcp") or (cdata == "udp")):
            tmpnum = int(cgrp)
            if((tmpnum <= 65535) and (tmpnum >= 1)):
                print("valid port")
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



if __name__ == "__main__":
    
    debug = 1

    inputfile = sys.argv[1]

    if(csvisgood(inputfile) == False):
        print("Existing program.  fix your input file")

"""
    with open(inputfile, newline='') as csvfile:
        csvreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in csvreader:
            row_type = row[0]
            row_data = row[1]
            row_grp  = row[2]            

            if(debug ==1):
                print(row_type, row_data, row_grp)
            try:
                if(rowisclean(row_type, row_data, row_grp)):
                    print("ROW IS CLEAN")
                else:
                    print("ROW IS INVALID")
            except:
                print("ROW IS INVALID")
"""
print("end")
