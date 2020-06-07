#
# Helping with 2.X to 3.X migrations where a unique management IP needed to be defined for each edge instead of 192.168.1.1
#
# Usage: VC_USERNAME='xxxx@velocloud.net' VC_PASSWORD='xxxxx' python XXXX.py
#

import os
import re
from client import *

# EDIT THESE
VCO_HOSTNAME = '10.165.193.209'
ENTERPRISE_ID = 1  # This is Customer ID, As may be found e.g. in web UI URL path under Customer



def main():
    client = VcoRequestManager(VCO_HOSTNAME)
    client.authenticate(os.environ['VC_USERNAME'], os.environ['VC_PASSWORD'],
                        is_operator=os.environ.get('VC_OPERATOR', True))

    # Input Edges modification CSV File

    file_name = raw_input("Please Input Edges File Name: ")+'.csv'
    print (file_name)

    fd = open(file_name, "r")
    lines = fd.readlines()
    for line in lines:
        line = line.strip()
        items = line.split(",")
        if items[0].isdigit() :
            edgeId = None
            edges = client.call_api('enterprise/getEnterpriseEdgeList', {'enterpriseId': ENTERPRISE_ID})
            target = [p for p in edges if p['name'] == items[1]][0]
            edgeId = target['id']

            print('### GETTING EDGE configuration ###')

            try:

                    res = client.call_api('edge/getEdgeConfigurationStack', {'enterpriseId': ENTERPRISE_ID, 'edgeId': edgeId})


            except Exception as e:
                    print('Failed to get configuration of Edge "%s"' % items[1])
                    print(e)

            edgeSpecificProfile = dict(res[0])
            edgeSpecificProfileDeviceSettings = [m for m in edgeSpecificProfile['modules'] if m['name'] == 'deviceSettings'][0]
            edgeSpecificProfileDeviceSettingsData = edgeSpecificProfileDeviceSettings['data']
            moduleId = edgeSpecificProfileDeviceSettings['id']

            # for validating an Ip-address 
            regex = '''^(25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.( 
            25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.( 
            25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)\.( 
            25[0-5]|2[0-4][0-9]|[0-1]?[0-9][0-9]?)'''

            print('### Updating Mgt IP ###')

            # Proceeding with Management IP changess if IP add format is correct
            if(re.search(regex, items[2])):

                    edgeSpecificProfileDeviceSettingsData['lan']['management'] = {'cidrIp': items[2], 'cidrPrefix': 32}

            #res = client.call_api('/configuration/updateConfigurationModule', {'enterpriseId': ENTERPRISE_ID, 'id': moduleId, '_update': {'data': edgeSpecificProfileDeviceSettingsData}})

                    try:

                                res = client.call_api('/configuration/updateConfigurationModule', {'enterpriseId': ENTERPRISE_ID, 'id': moduleId, '_update': {'data': edgeSpecificProfileDeviceSettingsData}})

                    except Exception as e:
                                print('Failed to update Mgt IP configuration of Edge "%s"' % items[1])
                                print(e)

            else:
                    print('Invalid IP address for Edge "%s"' % items[1])                     

if __name__ == '__main__':
    main()