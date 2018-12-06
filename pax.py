#
# Automation for promoting Endevor elements from D1 to P2.
# Uses python interface to Brightside (https://github-isl-01.ca.com/MFaaS/pybright)
#
from pybright.cli import bright

# import logging
# logging.basicConfig(level=logging.DEBUG)

def get_elements(sub, env, stage, debug=False):
    command = f"endevor list elements --sys AML020 --type * --env {env} --sn {stage}"
    if(sub!=""):
        command = f"{command} --sub {sub}"
    print(f">> bright {command}")
    elements = bright(command)  
    try:
        iter(elements)
        if(debug):
            for element in elements:
                print(element['elmName'], element['typeName'])
        return elements
    except TypeError:
        print('No elements found')
        return None

def promote_elements(elements, comment="pax automation", ccid="pax"):
    if(elements):
        for el in elements:
            if(el['typeName']!="SANDBOX"):
                command = f">> bright endevor move ele {el['elmName']} --type {el['typeName']} --env {el['envName']} --sn {el['stgNum']} --sys {el['sysName']} --cci {ccid} --com \"{comment}\" --sm"
                if(el['sbsName']):
                    command = f"{command} --sub {el['sbsName']}"
            print(command)  
            bright(command)

promote_elements(get_elements("AML02001", "DEV", 1))
promote_elements(get_elements("AML02001", "DEV", 2))
promote_elements(get_elements("", "QA", 2))
get_elements("", "PRD", 2, debug=True)
