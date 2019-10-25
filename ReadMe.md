# dcu-opentimetable 

Hello, I made this project due to the fact my old DCU timetable scraper stopped working due to the deprecation of the old system DCU used to display timetables.
This old system has now been replaced by [opentimetable](https://opentimetable.dcu.ie).

## Overview

This project can currently do the following:

- Pull information from a given location at a given hour.
    - Example usecase: see if a computing lab is free.
- Pull information from a given location for a time range.

## Installation 

The only extra required python module for this to work is *requests*.

> pip3 install requests

Besides that just git clone the repo and enjoy!

## Opentimetable Overview 

Opentimetable seems to work by assigning each location in DCU an *identifier*.
This *identifier* is used in requests to tell the system which location is being queried.
You can attach multiple identifiers to a single query.

> e.g. Check what is on at LG25, LG26, LG27 @ 16:00 - 17:00

There is a required "Authorization" header which is "basic T64Mdy7m["
I currently cannot find any information regarding this but it doesn't work if it's not there...

### The purpose of template.json 

template.json exists in order to act as a placeholder for the body of the post request sent to the API endpoint. This template is loaded into a dictionary and modifications are made onto it in order to form a valid request.

## Useful Scripts 

All scripts contain a single function that return a string with the requested value else an error.

By default running of these scripts this will print the return value of the associated function

#### checkfree.py 
Takes the current week and hour and checks if a room is booked at that time.

Input:

A single command line argument with a requested location on the glasnevin campus.

Output:

Whether the room is free at the given hour, what is currently on in the room or an error.

Usage:
> python3 checkfree.py LG25

Example output:
``` 
This lab is free :)
```

#### freerange.py 

Ths script takes 5 arguments, the room, the start time, the end time, the week and the day that you want to check if a room is free

There are two ways to give the script input:
- Via the CLI seperated by commas
    - `python3 freerange.py L125,10,11,5,5` ==> this will check L125 from 10-11 on week 5 Friday.
    - Additionally if you leave an argument black it will default to the current value
    - e.g `python3 LG25,,,,` will check if LG25 is free right now!
           - ***note*** if you leave end blank it will default to start +1 hour
Each of the 4 time parameters def
- Giving no command line arguments
    - This will then prompt you with questions like:
        - `What Room?: `
        - Leave the time parameters blank and they will default to current time(beside end which is start +1 hour)

Usage:
Check LG25 is free on Monday of week 7 from 10-11
Input:
`python3 freerange.py L128,10,,7,1`
Output:
`['CA318[1] Advanced Algorithms and A.I. Search\nStarted @10:00\nEnds @12:00\n'`


