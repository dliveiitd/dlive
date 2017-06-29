#!/usr/bin/env python
from __future__ import print_function
PKG_NAME = 'driverless_car'
import roslib; roslib.load_manifest(PKG_NAME)
import cv2
import geodesy.props
import geodesy.utm
import geodesy.wu_point
import rospy
import numpy as np
import itertools
from geodesy import bounding_box
from osm_cartography import xml_map
import yaml
import pickle

url="package://driverless_car/data/map(2).osm"
gmap = xml_map.get_osm(url, bounding_box.makeGlobal())
map = gmap
map_points = geodesy.wu_point.WuPointSet(gmap.points)
bbox = map.bounds
min_lat, min_lon, max_lat, max_lon = bounding_box.getLatLong(bbox)
p0 = geodesy.utm.fromLatLong(min_lat, min_lon).toPoint()
p1 = geodesy.utm.fromLatLong(min_lat, max_lon).toPoint()
p2 = geodesy.utm.fromLatLong(max_lat, max_lon).toPoint()
p3 = geodesy.utm.fromLatLong(max_lat, min_lon).toPoint()
print (p1.x-p0.x)
width=(p1.x-p0.x)*10
height=(p3.y-p0.y)*10
img=np.ones((height,width))*0


index = 0
for feature in itertools.ifilter(lambda(f): geodesy.props.match(f, set(['highway'])),
                                         map.features):
      index += 1
      prev_point = None
      for mbr in feature.components:
          wu_point = map_points.get(mbr.uuid)
          if wu_point:    
                  p = wu_point.toPointXY()
                  if prev_point:
                     cv2.line(img,(int((prev_point.x-p0.x)*10),int((prev_point.y-p0.y)*10)),(int((p.x-p0.x)*10),int((p.y-p0.y)*10)),(255,255,255),5)
                  prev_point=p

fs=['0.0','0.0','0.0']
map_meta={'image':"img2.jpg",'resolution':1.0,'origin':fs,'negate':0,'occupied_thresh':0.65,'free_thresh':0.196}
f=open('imgdm.yaml', 'w') 
f.write('image: imgdm.jpg\nresolution: 0.1\norigin: [0.0,0.0,0.0]\noccupied_thresh: 0.65\nnegate: 0\nfree_thresh: 0.196')
f.close()
#yaml.dump(map_meta, f)
cv2.imwrite("imgdm.jpg",img)
#f=open("/home/rohit/Downloads/test.save","rb")
#way_point=pickle.load(f)
#for i in xrange(len(way_point)):
#	p=geodesy.utm.fromLatLong(way_point[i][0], way_point[i][1]).toPoint()
	
#	cv2.circle(img,(int(p.x-p0.x),int(p.y-p0.y)),10,(128,128,128),-1)

#cv2.imshow("img",img)
#cv2.waitKey(0)
#cv2.imwrite("img3.jpg",img)

