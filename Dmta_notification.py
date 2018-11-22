from google.transit import gtfs_realtime_pb2
import requests
import time # imports module for Epoch/GMT time conversion
import os # imports package for dotenv
import settings

#from dotenv import load_dotenv, find_dotenv # imports module for dotenv
#load_dotenv(find_dotenv()) # loads .env from root directory

# The root directory requires a .env file with API_KEY assigned/defined within
# and dotenv installed from pypi. Get API key from http://datamine.mta.info/user


API_KEY="6d8b5a1c30d0d0b6666d16cd7736df84"


api_key = API_KEY

# Requests subway status data feed from City of New York MTA API
feed = gtfs_realtime_pb2.FeedMessage()
response = requests.get('http://datamine.mta.info/mta_esi.php?key={}&feed_id=21'.format(api_key))

#print(response.content)

feed.ParseFromString(response.content)

#print(feed)


# The MTA data feed uses the General Transit Feed Specification (GTFS) which
# is based upon Google's "protocol buffer" data format. While possible to
# manipulate this data natively in python, it is far easier to use the
# "pip install --upgrade gtfs-realtime-bindings" library which can be found on pypi

from protobuf_to_dict import protobuf_to_dict

subway_feed = protobuf_to_dict(feed) # subway_feed is a dictionary

#print(subway_feed)


realtime_data = subway_feed['entity'] # train_data is a list



# Because the data feed includes multiple arrival times for a given station
# a global list needs to be created to collect the various times
collected_times = []

# This function takes a converted MTA data feed and a specific station ID and
# loops through various nested dictionaries and lists to (1) filter out active
# trains, (2) search for the given station ID, and (3) append the arrival time
# of any instance of the station ID to the collected_times list
def station_time_lookup(train_data, station):
	for trains in train_data: # trains are dictionaries
		print(trains)	
		if trains.get('trip_update', False) != False:
			unique_train_schedule = trains['trip_update'] # train_schedule is a dictionary with trip and stop_time_update
			unique_arrival_times = unique_train_schedule['stop_time_update'] # arrival_times is a list of arrivals
			for scheduled_arrivals in unique_arrival_times: #arrivals are dictionaries with time data and stop
				if scheduled_arrivals.get('stop_id', False) == station:
					time_data = scheduled_arrivals['arrival']
					unique_time = time_data['time']
					if unique_time != None:
						collected_times.append(unique_time)

# Run the above function for the station ID for Broadway-Lafayette
#station_time_lookup(realtime_data, 'D21S')

station_time_lookup(realtime_data, 'D20S')

# Sort the collected times list in chronological order (the times from the data
# feed are in Epoch time format)
collected_times.sort()

# Pop off the earliest and second earliest arrival times from the list
nearest_arrival_time = collected_times[0]
second_arrival_time = collected_times[1]

if (nearest_arrival_time <0):
	nearest_arrival_time = 0

# Grab the current time so that you can find out the minutes to arrival
current_time = int(time.time())
time_until_train = int(((nearest_arrival_time - current_time) / 60))

# This final part of the code checks the time to arrival and prints a few
# different messages depending on the circumstance
print("\n\n\n")
##if time_until_train > 10:

time_until_next_train = int(((second_arrival_time - current_time) / 60))
print("It is currently " + time.strftime("%I:%M %p"))
print("\nThe next Brooklyn-bound F train from W4 Street Station arrives in "+str(time_until_train) +" minutes at " + time.strftime("%I:%M %p", time.localtime(nearest_arrival_time)))

print("\nThe next one after that arrives in "+ str(time_until_next_train) + " minutes at " + time.strftime("%I:%M %p", time.localtime(second_arrival_time)))


# These are useful print statments used for script debugging, commented out
#
# for times in collected_times:
     # print(times, "=", time.strftime("%I:%M %p", time.localtime(times)))
# print(collected_times)
# print(nearest_arrival_time)
# print(second_arrival_time)
# print(time_until_train)


