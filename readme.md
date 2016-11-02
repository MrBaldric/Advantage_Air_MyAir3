#Advantage Air MyAir3 Ducted Airconditioner monitoring
This program was written to log the temperatures around the house from the room sensors that are attached to my MyAir3 AC system and store them in a postgresql database.

The data captured in the database was then used to produce a daily max and min temperature report. 

There is more you can do with the MyAir3 Api like turn Air on and off and control zones but i have not looked in to that part with this script.

The control and monitoring is all done through HTML requests.

I also had a web page accessing the postgresql database which displayed live temperatures in each room as the 
app that was provided didn't show this at all.
