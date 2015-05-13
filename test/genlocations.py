from __future__ import division
import random
import sys
import math


def generate_locations(radius=10000, datacount=100,slat=40.84, slng=-73.87):


    radiusInDegrees = radius/111300

    r = radiusInDegrees
	

    for i in range(1,datacount):
		
        u = float(random.uniform(0.0,1.0))
        v = float(random.uniform(0.0,1.0))
		
        w = r * math.sqrt(u)
        t = 2 * math.pi * v
        x = w * math.cos(t)
        y = w * math.sin(t)

		
        xLat = x + slat
        yLng = y + slng
		
        print str(xLat) +  "," + str(yLng)
