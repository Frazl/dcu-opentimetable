import timetable 
import sys
import datetime

def main(room):
    #Get all the weeks from the main website 
    week_lis = timetable.get_weeks()
    # The start of the week is needed for the site to know what week we are querying 
    weekstart = timetable.get_start_current_week(week_lis)
    # The current day of the week is needed so can get the correct day 
    # ISO weekday returns 7 for sunday when the site represents that as 0 hence modulus
    weekday = datetime.datetime.now().isoweekday() % 6 
    # Get the current hour 
    hour = datetime.datetime.now().hour
    # Each room has a unique ID and so we need to fetch them 
    GLA_identities = timetable.request_GLA_idendities()
    # Map each room to it's ID 
    identity_map = timetable.build_identity_map(GLA_identities)
    try:
        room_id = identity_map[room]
    except KeyError:
        return("This is not a valid room / the room was not found. :(")
    template = timetable.load_template()
    required_data = timetable.build_template(template, room_id, weekstart, weekday, hour, hour + 1)
    ongoing = timetable.request_events(room_id, required_data)
    for event in ongoing:
        start = event['StartDateTime']
        end = event['EndDateTime']
        module_name = event['ExtraProperties'][0]['Value']
        return timetable.found_event(module_name, start, end)
    return("This lab is free! :)")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(main(sys.argv[1]))
    else:
        print("Please supply a valid location. e.g. LG25")