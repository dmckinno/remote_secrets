import os
import numpy
import numpy as np
import numpy as N
from numpy import genfromtxt
import random
import requests
import json
import time

# This function imports an image from within the directory that the script is run.

your_directory = os.getcwd()+"/"


def import_image():
    image_variable = str(random.randint(1, 10000))

    image_name = raw_input("Which scene would you like to analyze? Note that it must be in this root directory.")

    mask_name = raw_input("Which file would you like to use to mask your scene? Note that it must be in this root directory.")

    # Clip the image with gdalwarp
    # You must hahe gdal installed for this script to work
    os.system("gdalwarp -q -cutline "+your_directory+mask_name+" -crop_to_cutline -dstalpha -tr 0.1 0.1 -of GTiff "+your_directory+image_name+" "+your_directory+image_variable+".tif")

    # Turn the tiff into a text file
    os.system("gdal_translate -of XYZ "+your_directory+image_variable+".tif "+your_directory+image_variable+".xyz")
    print "gdal_translate -of XYZ "+your_directory+image_variable+".tif "+your_directory+image_variable+".xyz"

    data = genfromtxt(image_variable+".xyz", delimiter=' ')

    return data

# This function turns the image into a array and sorts by intensity.

def sort_by_intensity(data):

    data = np.array(data)

    data = data[data[:,2].argsort()]

    # This function writes the n most intense rows to a csv

    number_of_entries = raw_input("How many entries do you want to return?")

    data = data[-int(number_of_entries):,:]

    numpy.savetxt("sorted_data.csv", data, delimiter=",")
 
# This function loops over the array, calls the Google Places API, and appends the name as another column.
    n=-1
    place=[]

    while n >= -int(number_of_entries):
        location = requests.get("https://maps.googleapis.com/maps/api/place/nearbysearch/json?location="+str(data[n,1])+","+str(data[n,0])+"&radius=5000&key=YOUR_API_KEY")
        response = json.loads(location.text)
        if response["status"] != "ZERO_RESULTS":
            print(response["results"][0]["vicinity"])
            place.append(response["results"][0]["vicinity"].encode('ascii', 'ignore').decode('ascii'))
        else:
            print("There is no information available about this place.")
            place.append("There is no information available about this place.")
        n = n-1
    
    a = place[::-1]

    mapbox_array = [a,data[:,1],data[:,0],data[:,2]]
    mapbox_array = zip(*mapbox_array)
    header = ["title","lat","lon","intensity"]
    mapbox_array_header = numpy.vstack([header, mapbox_array])
    print mapbox_array_header
    numpy.savetxt("mapbox.csv", mapbox_array_header, delimiter=",", fmt="%s")
    
    


def google_custom_search(data):
	
    news = requests.get("https://www.googleapis.com/customsearch/v1?key=YOUR_API_KEY&cx=011812869797907996842%3Aczujyeamqbq&q="+data+"&start=1")
    news_reader = json.loads(news.text)
    print("Number of results")
    print(news_reader["searchInformation"]["totalResults"])
    
    if int(news_reader["searchInformation"]["totalResults"]) != 0:
        print("Headline")
        print(news_reader["items"][0]["title"])
        print(news_reader["items"][0]["snippet"])
    else:
        print("No one knows what's going on in "+data)


sort_by_intensity(import_image())