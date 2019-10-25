import timetable 
import sys
import datetime

def week_start_calc(week_lis, weeknum):
    if weeknum != "":
        # This finds the start of the week that you specified
        return(timetable.get_start_target_week(week_lis, weeknum))
    else:
        # This finds the start of the current week
        return(timetable.get_start_current_week(week_lis))

def day_calc(day):
    if day != "":
        # This selects the days as you specify
        return(int(day))
    else:
        # This takes the current day
        return(datetime.datetime.now().isoweekday() % 6)

def start_calc(start):
    if start != "":
        return int(start)
    else:
        return datetime.datetime.now().hour

def end_calc(end, start):
    if end != "":
        return int(end)
    else:
        return start + 1

def main(room, start = "", end = "", weeknum = "", day= ""):
    #Get all the weeks from the main website 
    week_lis = timetable.get_weeks()
    weeknum = week_start_calc(week_lis, weeknum) # The start of the week is needed for the site to know what week we are querying 
    weekday = day_calc(day) # The day of the week is needed so can get the correct day 
    start = start_calc(start)# The start time ==> defaults to current time if left null 
    end = end_calc(end, start)# The end time ==> defaults to current time if left null
    # ISO weekday returns 7 for sunday when the site represents that as 0 hence modulus
    # Each room has a unique ID and so we need to fetch them 
    GLA_identities = timetable.request_GLA_idendities()
    # Map each room to it's ID 
    identity_map = timetable.build_identity_map(GLA_identities)
    try:
        room_id = identity_map[room]
    except KeyError:
        return("This is not a valid room / the room was not found. :(")
    template = timetable.load_template()
    required_data = timetable.build_template(template, room_id, weeknum, weekday, start, end)
    ongoing = timetable.request_events(room_id, required_data)
    if ongoing:
        lis = []
        for event in ongoing:
            start = event['StartDateTime']
            end = event['EndDateTime']
            module_name = event['ExtraProperties'][0]['Value']
            lis.append(timetable.found_event(module_name, start, end))
        return lis
    else:
        return "This lab is free for the period! :)"

if __name__ == "__main__":

    if len(sys.argv) > 1:
        print(main(*sys.argv[1:][0].split(",")))
    else:
        print(main(input("Room Number: "), input("Start Time: "), input("End Time: "), input("Week Number: "), input("Day(Sunday = 0): ")))
