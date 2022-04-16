#!/usr/bin/env python


# The fleets require a firewall(iptables) which allows different fleets access to different ports on the hosts:
#    5141 - Logstash rsyslog port on logs.*, required access from ALL hosts.
#    9100 - Node exporter on ALL hosts, required access by metrics.*.
#    9104 - MySQL exporter on app.* hosts, required access by metrics.*.
#    3306 - MySQL database on app.*, requried access by backups.*.


import json
import subprocess

# Open a file
consulOutput = open("./test-data/services.json", "r+")

jsonData = json.loads(consulOutput.read())
consulOutput.close()

environments = ["test", "prod"]
fleets = ["metrics", "logs", "backups", "app"]

def createIPset(IPsetName):
    command = [
            "firewall-cmd", "--permanent", "--new-ipset="+IPsetName, "--type=hash:net"
            ]
    return subprocess.Popen(command, shell=False, stdout=subprocess.PIPE).stdout.read()

def getIPsetList():
    command = [
            "firewall-cmd", "--permanent", "--get-ipsets"
            ]
    return subprocess.Popen(command, shell=False, stdout=subprocess.PIPE).stdout.read()


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

print(getFleetNamesFromJson(jsonData, "test"))
jsonIPs = getFleetIPsFromJson(jsonData, "test", "app")
print(jsonIPs)
currentIP = ['10.0.0.1', '10.0.0.2', '10.10.0.61']
print("Remove IPs: " + str(getExtraItemsfromlists(currentIP, jsonIPs)) )
print("Add IPs: " + str(getMissingItemsfromlists(currentIP, jsonIPs)) )
