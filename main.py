# -*- coding: utf-8 -*-
import json

import requests

try:
    from wox import Wox as FlowLauncher
except ModuleNotFoundError:
    from flowlauncher import FlowLauncher




        else:
        try:
        except:
            pass


    def context_menu(self, data):
        results = []
        results.append({
            "Title": "test",
            "SubTitle": "test",
            #"IcoPath":ico,
            "JsonRPCAction": {
                #change query to show only service type
                "method": "Wox.ChangeQuery",
                "parameters": ["ha" + " " + keywords, False],
                # hide the query wox or not
                "dontHideAfterAction": True
            }
        })
        return results

    def query(self, query):
        results = []
        argument = ""
        argument = query.split()
        #---handle connection errors
        if len(argument) >= 1:
            for keywords in key_services:
                title = keywords
                subtext = keywords
                ico = './icons/icons_' + icon_color + "/filter.png"
                if query.strip().lower() in keywords.lower():
                    #---add filters to results
                    if argument[0] not in key_services:
                        results.append({
                            "Title": "Filter by: [" + keywords + "]",
                            "SubTitle": "show " + keywords + " services only",
                            "IcoPath":ico,
                            "JsonRPCAction": {
                                "method": "Wox.ChangeQuery",
                                "parameters": ["ha" + " " + keywords, True],
                                "dontHideAfterAction": True
                            }
                        })
            service = get_entity(argument[0])
            if service == -1:
                WoxAPI.change_query("ha connection error",True)
            for x in range(0, len(service)):
                entity_id = service[x]["entity_id"]
                try:
                    title = service[x]["attributes"]["friendly_name"]
                except:
                    title = entity_id
                state = service[x]["state"]
                try:
                    unit_of_measurement = service[x]["attributes"]["unit_of_measurement"]
                    state += unit_of_measurement
                except:
                    pass
                ico = get_icon(entity_id,state)
                subtext = get_attributes(service,x)
                #----Check if user is refrencing a service keyword and filters it out of query
                if argument[0].rstrip("s") in key_services:
                    if query.replace(argument[0],"",1).strip().lower() in title.lower():
                        results.append({
                            "Title": title + " is " + '\"' + state + '\"',
                            "SubTitle": subtext,
                            "IcoPath":ico,
                            "JsonRPCAction":{
                              "method": "activate",
                              "parameters":[entity_id,title,query],
                              "dontHideAfterAction":True,
                            }
                        })
                else:
                    #----check if query matches any results
                    if query.lower().strip() in title.lower():
                        results.append({
                            "Title": title + " is " + '\"' + state + '\"',
                            "SubTitle": subtext,
                            "IcoPath":ico,
                            "JsonRPCAction":{
                              "method": "activate",
                              "parameters":[entity_id,title,query],
                              "dontHideAfterAction":True
                            }
                        })
                #----Check to see if only one match and if exact match of title (No false positives when using filters)
                if query.lower().strip().startswith(title.lower()):
                    results = []
                    #----Add entry for every attribute
                    if not query.lower().replace(title.lower(),"",1).strip().startswith("info".lower()):
                        if get_type(entity_id) == "light":
                            ico = get_icon(entity_id, state)
                            percentage = query.lower().replace(title.lower(),"",1).strip()
                            results.append({
                                "Title": "Adjust Brightness",
                                "SubTitle": "Adjust brightness level to " + query.replace(title.lower(),"",1).lower().strip() + "%",
                                "IcoPath":ico,
                                "JsonRPCAction":{
                                  "method": "adjust_brightness",
                                  "parameters":[entity_id,percentage],
                                  "dontHideAfterAction":True
                                }
                            })
                            results.append({
                                "Title": "Toggle",
                                "SubTitle": "Toggle " + title,
                                "IcoPath":ico,
                                "JsonRPCAction":{
                                  "method": "activate",
                                  "parameters":[entity_id,title,query],
                                  "dontHideAfterAction":True
                                }
                            })
                        else:
                            results.append({
                                "Title": "Action",
                                "SubTitle": "Activate default action for " + get_type(entity_id),
                                "IcoPath":ico,
                                "JsonRPCAction":{
                                  "method": "activate",
                                  "parameters":[entity_id,title,query],
                                  "dontHideAfterAction":True
                                }
                            })
                        if subtext != "N/A":
                            ico = './icons/icons_' + icon_color + '/info.png'
                            results.append({
                                "Title": "Info",
                                "SubTitle": "Show detailed information",
                                "IcoPath":ico,
                                "JsonRPCAction": {
                                    "method": "Wox.ChangeQuery",
                                    "parameters": ["ha " + query + " info" , True],
                                    "dontHideAfterAction": True
                                }
                            })
                    if query.lower().replace(title.lower(),"",1).strip().startswith("info".lower()):
                        results = []
                        for g in range(len(service[x]["attributes"].keys())):
                            key = list(service[x]["attributes"].keys())[g].replace("_"," ")
                            value = service[x]["attributes"].values()[g]
                            try:
                                value = removeNonAscii(value)
                            except:
                                value = value
                            ico = './icons/icons_' + icon_color + '/info.png'
                            if key != "friendly name" and key != "unit of measurement":
                                if query.lower().replace(title.lower(),"",1).replace("info","",1).lower().strip().lower() in str(value).lower().strip().lower():
                                    results.append({
                                        "Title": value,
                                        "SubTitle": key,
                                        "IcoPath": ico,
                                        "JsonRPCAction": {
                                            "method": "Wox.ChangeQuery",
                                            "parameters": [str(key) + ": " + str(value), True],
                                            "dontHideAfterAction": True
                                        }
                                    })
        #----No user input except action word
        else:
            for keywords in key_services:
                title = keywords
                subtext = keywords
                ico = './icons/icons_' + icon_color + "/filter.png"
                results.append({
                    "Title": "Filter by: [" + keywords + "]",
                    "SubTitle": "show " + keywords + " services only",
                    "IcoPath":ico,
                    "JsonRPCAction": {
                        #change query to show only service type
                        "method": "Wox.ChangeQuery",
                        "parameters": ["ha" + " " + keywords, False],
                        # hide the query wox or not
                        "dontHideAfterAction": True
                    }
                })


        return results

if __name__ == "__main__":
    Commander()
