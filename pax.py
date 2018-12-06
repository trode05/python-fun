#
# Automation for promoting Endevor elements from D1 to P2.
# Uses python interface to Brightside (https://github-isl-01.ca.com/MFaaS/pybright)
#
from pybright.cli import bright

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

def promote_elements(elements):
    for element in elements:
        if(element['typeName']!="SANDBOX"):
            command = f">> bright endevor move ele {element['elmName']} --type {element['typeName']} --sn {element['stgNum']}"
        print(command)  

promote_elements(get_elements("AML02001", "DEV", 1))
promote_elements(get_elements("AML02001", "DEV", 2))
promote_elements(get_elements("", "QA", 2))
promote_elements(get_elements("", "PRD", 2))
