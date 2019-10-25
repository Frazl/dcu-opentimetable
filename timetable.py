import requests 
import json
import logging
from functools import reduce
import datetime
import sys 


global HEADERS
HEADERS = {
    "Authorization": "basic T64Mdy7m[",
    "Content-Type" : "application/json; charset=utf-8",
    "credentials": "include",
    "Referer" : "https://opentimetable.dcu.ie/",
    "Origin" : "https://opentimetable.dcu.ie/"
}

def parse_date(date_str):
    '''
    Parses the date to a datetime date object
    '''
    year = int(date_str[:4])
    month = int(date_str[5:7])
    day = int(date_str[8:10])
    return datetime.datetime(year, month, day).date()
    
def get_start_target_week(week_lis, weeknum):
    '''
    Gets the start date for the target week
    '''
    if int(weeknum) <=12:
        semester_start = datetime.datetime(2019,9,23).date()
        return semester_start + datetime.timedelta(weeks = int(weeknum)-1)
    elif int(weeknum) <= 24:
        semester_start = datetime.datetime(2020,1,27).date()
        return semester_start + datetime.timedelta(weeks = int(weeknum)-20)

def get_start_current_week(week_lis):
    '''
    Gets the start date for the current week 
    '''
    curr = datetime.datetime.now().date()
    i = 0 
    while curr not in week_lis and i < 14:
        curr = curr - datetime.timedelta(days=1)
        i += 1
    return curr

def get_hour_as_string(time):
    s = str(time) + ":00"
    if len(s) != 5:
        s = "0" + s 
    return s

def get_weeks(): 
    '''
    Queries the site for the weeks and returns it as a dictionary object
    '''
    res = requests.get("https://opentimetable.dcu.ie/broker/api/viewOptions", headers=HEADERS)
    weeks = json.loads(res.text)['Weeks']
    week_lis = []
    for i in range(len(weeks)):
        s = weeks[i]['FirstDayInWeek']
        week = parse_date(s)
        week_lis.append(week)
    return week_lis

def request_GLA_idendities():
    '''
    Get's the associated identity of each room on the glasnevin campus
    '''
    required_data = {
        "Identity": "6359fd0c-1bbe-496a-8998-4fefc5cd18de",
        "Values": ["2ebced11-707f-0aca-6477-a30a0c43aa70"]
    }
    res = requests.post("https://opentimetable.dcu.ie/broker/api/CategoryTypes/1e042cb1-547d-41d4-ae93-a1f2c3d34538/Categories/Filter?pageNumber=1", json=required_data, headers=HEADERS)
    d = json.loads(res.text)

    results = []
    results.append(d['Results'])

    total_pages = int(d['TotalPages'])
    logging.info('Found %s total pages', total_pages)
    for i in range(2, total_pages+1):
        logging.debug("fetching identities for GLA page - %s", i)
        res = requests.post("https://opentimetable.dcu.ie/broker/api/CategoryTypes/1e042cb1-547d-41d4-ae93-a1f2c3d34538/Categories/Filter?pageNumber="+str(i), json=required_data, headers=HEADERS)
        if res.status_code != 200:
            logging.critical("Page %s could not be loaded! Not all identities may have been captured", i)
        d = json.loads(res.text)
        results.append(d['Results'])
    logging.info('Pulled results for %s total pages', total_pages)
    return reduce(lambda x,y :x+y, results )


def build_identity_map(identities_lis):
    '''
    Maps a room name to an identify number given a list of identities
    '''
    id_map = {}
    for identitiy in identities_lis:
        #Split to get GLA only rooms 
        l = identitiy['Name'].split(".")
        if l[0] == 'GLA':
            id_map[l[1]] = identitiy['Identity']
    return id_map


def load_template(name='template.json'):
    '''
    Loads the given template file which is used the data of the post request.
    '''
    with open('template.json', 'r') as f:
        template = json.load(f)
    
    return template

def build_template(template, room_id, weekstart, weekday, start_time, end_time):
    '''
    Builds on top of the template for the default post request
    '''
    template['CategoryIdentities'][0] = room_id
    template['ViewOptions']['Days'][0]['DayOfWeek'] = weekday
    template['ViewOptions']['TimePeriods'][0]['StartTime'] = get_hour_as_string(start_time)
    template['ViewOptions']['TimePeriods'][0]['EndTime'] = get_hour_as_string(end_time)
    
    weekstart = str(weekstart).split(" ")
    weekstart = "-".join(weekstart) + "T00:00:00.000Z"
    template['ViewOptions']['Weeks'][0]['FirstDayInWeek'] = weekstart
    return template

def request_events(room_id, data):
    res = requests.post("https://opentimetable.dcu.ie/broker/api/categoryTypes/1e042cb1-547d-41d4-ae93-a1f2c3d34538/categories/events/filter", json=data, headers=HEADERS)
    if res.status_code != 200:
        logging.critical("Unable to get request for room with ID: %s", room_id)
        return("Unable to access timetable... might be down? :(")
    else:
        logging.debug("Succesfully got request for room with ID: %s", room_id)
        result = json.loads(res.text)
        ongoing = result[0]['CategoryEvents']
        return ongoing


def fetch_room_info(room_id, weekstart, weekday, start_time, end_time):
    '''
    Get's information about a room at a given time and date.
    '''
    #Change the default example to the requested paramaters
    template = load_template()
    required_data = build_template(template, room_id, weekstart, weekday, start_time, end_time)
    ongoing = request_events(room_id, required_data)
    for event in ongoing:
        start = event['StartDateTime']
        end = event['EndDateTime']
        module_name = event['ExtraProperties'][0]['Value']
        return found_event(module_name, start, end)
    return("This lab is free! :)")


def found_event(module_name, start, end):
    s = module_name + "\n"
    s += "Started @" + start.split("T")[1][:5] + "\n"
    s += "Ends @" + end.split("T")[1][:5] + "\n"
    return(s)
