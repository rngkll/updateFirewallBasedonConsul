#!/usr/bin/env python

import sys, getopt
import json
import subprocess
import requests

def getHostname():
    command = [
            "hostname", "-f"
            ]
    result = subprocess.Popen(command, shell=False, stdout=subprocess.PIPE).stdout.read()
    return bytes(result).decode('utf-8')

def reloadFirewalld():
    command = [
            "firewall-cmd", "--reload"
            ]
    result = subprocess.Popen(command, shell=False, stdout=subprocess.PIPE).stdout.read()
    return bytes(result).decode('utf-8')

def addFirewalldIPsetRule(zone, sourceIPset):
    command = [
            "firewall-cmd", "--permanent", "--zone="+zone, "--add-source=ipset:"+sourceIPset
            ]
    result = subprocess.Popen(command, shell=False, stdout=subprocess.PIPE).stdout.read()
    return bytes(result).decode('utf-8')

def addFirewalldPortRule(zone, port, protocol):
    command = [
            "firewall-cmd", "--permanent", "--zone="+zone, "--add-port="+port+"/"+protocol
            ]
    result = subprocess.Popen(command, shell=False, stdout=subprocess.PIPE).stdout.read()
    return bytes(result).decode('utf-8')

def allowSourceandPort(zone, sourceIPset,port, protocol):
        print(addFirewalldIPsetRule(zone, sourceIPset))
        print(addFirewalldPortRule(zone, port, protocol))

def createIPset(IPsetName):
    command = [
            "firewall-cmd", "--permanent", "--new-ipset="+IPsetName, "--type=hash:net"
            ]
    result = subprocess.Popen(command, shell=False, stdout=subprocess.PIPE).stdout.read()
    return bytes(result).decode('utf-8')

def getIPsetList():
    command = [
            "firewall-cmd", "--permanent", "--get-ipsets"
            ]
    result = subprocess.Popen(command, shell=False, stdout=subprocess.PIPE).stdout.read()
    return bytes(result).decode('utf-8').split()

def getIPsetEntries(ipsetName):
    command = [
            "firewall-cmd", "--permanent", "--ipset="+ipsetName, "--get-entries"
            ]
    result = subprocess.Popen(command, shell=False, stdout=subprocess.PIPE).stdout.read()
    return bytes(result).decode('utf-8').split()

def addIPsetEntry(ipsetName, entry):
    command = [
            "firewall-cmd", "--permanent", "--ipset="+ipsetName, "--add-entry="+entry
            ]
    result = subprocess.Popen(command, shell=False, stdout=subprocess.PIPE).stdout.read()
    return bytes(result).decode('utf-8')

def removeIPsetEntry(ipsetName, entry):
    command = [
            "firewall-cmd", "--permanent", "--ipset="+ipsetName, "--remove-entry="+entry
            ]
    result = subprocess.Popen(command, shell=False, stdout=subprocess.PIPE).stdout.read()
    return bytes(result).decode('utf-8')

def getFleetNamesFromJson(jsonData, environment):
    fleetList = []
    for item in jsonData:
        if item["NodeMeta"]["stage"] == environment:
            try:
                fleetList.append(item['NodeMeta'].get('env'))
            except KeyError:
                print("Error getting fleet name from json")
    return list(set(fleetList))

def getFleetIPsFromJson(jsonData, environment, fleetName):
    IPlist = []
    for item in jsonData:
        if item["NodeMeta"]["stage"] == environment and item["NodeMeta"]["env"] == fleetName:
            try:
                IPlist.append(item.get('ServiceAddress'))
            except KeyError:
                print("Error getting fleet IP from json")
    return list(set(IPlist))

def getExtraItemsfromlists(li1, li2):
    return list(set(li1) - set(li2))

def getMissingItemsfromlists(li1, li2):
    return list(set(li2) - set(li1))

def updateFirewallBasedOnConsul(stage, zone, jsonData):
    currentIPsets = getIPsetList()
    consulIPsets = getFleetNamesFromJson(jsonData, stage)
    missingIPsets = getMissingItemsfromlists(currentIPsets, consulIPsets)

    for item in missingIPsets:
        print("Creating IPset for fleet: " + str(item))
        createIPset(item)

    for ipsetItem in getIPsetList():
        currentIPsInSet = getIPsetEntries(ipsetItem)
        jsonIPs = getFleetIPsFromJson(jsonData, stage, ipsetItem)
        print("Add missing IPs in: " + ipsetItem)
        for entry in getMissingItemsfromlists(currentIPsInSet, jsonIPs):
            addIPsetEntry(ipsetItem, entry)
            print("added: "+ entry + " to fleet: " + ipsetItem)

        print("Remove extra IPs in: " + ipsetItem)
        for entry in getExtraItemsfromlists(currentIPsInSet, jsonIPs):
            removeIPsetEntry(ipsetItem, entry)
            print("Removed: "+ entry + " from fleet: " + ipsetItem)

    hostName = getHostname()

    #    9100 - Node exporter on ALL hosts, required access by metrics.*.
    firewallChange = allowSourceandPort(zone, "metrics", "9100", "tcp")
    print("firewallChange")
    #    5141 - Logstash rsyslog port on logs.*, required access from ALL hosts.
    if "logs" in hostName:
        for item in getIPsetList():
            firewallChange = allowSourceandPort(zone, item, "5141", "udp")
            print("firewallChange")
    elif "app" in hostname:
        #    9104 - MySQL exporter on app.* hosts, required access by metrics.*.
        firewallChange = allowSourceandPort(zone, "metrics", "9104", "tcp")
        print("firewallChange")
        #    3306 - MySQL database on app.*, requried access by backups.*.
        firewallChange = allowSourceandPort(zone, "backups", "3306", "tcp")
        print("firewallChange")

    # Reload firewalld to apply changes
    print("Reloading firewalld: " + reloadFirewalld())

def main(argv):
    stage = ''
    zone = ''
    url = ''
    try:
        opts, args = getopt.getopt(argv,"hs:z:u:",["stage=","zone=", "url="])
    except getopt.GetoptError:
        print ('configureFirewall.py -s <stage> -z <zone> -u <consuldataURL>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print ('configureFirewall.py -s <stage> -z <zone> -u <consuldataURL>')
            sys.exit()
        elif opt in ("-s", "--stage"):
            stage = arg
        elif opt in ("-z", "--zone"):
            zone = arg
        elif opt in ("-u", "--url"):
            url = arg

    # Open a file
    consulOutput = open("./test-data/services.json", "r+")
    jsonData = json.loads(consulOutput.read())
    consulOutput.close()

    # Uncomment for using API request
    #response = requests.get(url)
    #jsonData = response.json()

    updateFirewallBasedOnConsul(stage, zone, jsonData)


if __name__ == "__main__" :
    main(sys.argv[1:])
