#! /usr/bin/env python
"""
Created on Sun Jun 18 14:08:06 2017

@author: rohit
"""

import cv2
import rospy
import numpy as np
from nav_msgs.msg import Odometry
from driverless_car.msg import more
from driverless_car.msg import random
import sys, select, termios, tty
import tf
def createLineIterator(P1, P2, img):
    print "start",P1
    print "end",P2
    move=[[1,0],
          [-1,0],
          [0,1],
          [0,-1],
          [1,1],
          [1,-1],
          [-1,1],
          [-1,-1]]
    itera=True
    rec=more()
    ran=random()
    
    ran.x=P1[0]
    ran.y=P1[1]
    rec.msg.append(ran)
    
    universal_list=[]
    universal_list.append([P1[0],P1[1]])
    prevx=-1
    prevy=-1
    while itera==True:
        for i in range(0,8):
            x=P1[0]+move[i][0]
            y=P1[1]+move[i][1]
            print x
            print y
        
            if x>=0 and y>=0 and x<img.shape[0] and y<img.shape[1] and (x!=prevx or y!=prevy):
                if img[y,x,0]==255 and img[y,x,1]==0 and img[y,x,2]==0:
                    universal_list.append([x,y])
                    prevx=P1[0]
                    prevy=P1[1]
                    P1[0]=x
                    P1[1]=y
                    ran=random()
                    ran.x=P1[0]
                    ran.y=P1[1]
                    rec.msg.append(ran)
                    print P1
                    break
        if P1[0]==P2[0] and P1[1]==P2[1]:
            itera=False
    
   # while (1):
         #key=getKey()
    pub.publish(rec)
         #if (key == '\x03'):
          #   break
    return universal_list
def draw_path(event,x,y,flags,param):
    global all_intialisation_done
    global coord_prev
    global left_press
    global img
    global prev_img
    global press_first
    global temp_prev
    if all_intialisation_done==True:
        
        if event == cv2.EVENT_LBUTTONDOWN:
           if press_first==False:
              prev_img=img.copy()
              coord_prev[2]=coord_prev[0]
              coord_prev[3]=coord_prev[1]
           if left_press==True:
              cv2.line(img,(int(coord_prev[0]),int(coord_prev[1])),(int(x),int(y)),[255,0,0],1)
              print "distance",np.sqrt((x-coord_prev[0])**2+(y-coord_prev[1])**2)
              coord_prev[0]=x
              coord_prev[1]=y
              press_first=False
              
              
     
           
def callback(data):
    global dummy
    global odom_data_recv
    dummy=data
    odom_data_recv=True
def getKey():
    tty.setraw(sys.stdin.fileno())
    rlist, _, _=select.select([sys.stdin], [], [], 0.1)
    if rlist:
       key = sys.stdin.read(1)
    else:
       key='q'
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
    return key
cv2.namedWindow("waypoint_planner",0)
settings = termios.tcgetattr(sys.stdin)
img=cv2.imread("/home/rohit/scratch/src/driverless_car/maps/fivem.jpg",cv2.IMREAD_COLOR)
cv2.setMouseCallback('waypoint_planner',draw_path)
rospy.init_node('will_name_it_later', anonymous=True)
pub = rospy.Publisher('way_msg', more, queue_size=10)
odom_map_tf=tf.TransformListener()
#rospy.Subscriber('odom', Odometry, callback)
initial_point=False
odom_data_recv=False
transform_rec=False
all_intialisation_done=False
left_press=True
coord_prev=[0,0,0,0]
prev_img=1
press_first=True
dummy=Odometry()
temp_prev=0
show_plot=False
while not rospy.is_shutdown():
    key=getKey()
    if key=="z":
        initial_point=True
        dummy=rospy.wait_for_message('odom',Odometry)
        odom_data_recv=True
        print dummy
    try:
            [trans,rot] = odom_map_tf.lookupTransform('/map', '/odom', rospy.Time(0))
            transform_rec=True
    except (tf.LookupException, tf.ConnectivityException, tf.ExtrapolationException):
            transform_rec=False
            continue
        
    if (initial_point==True and odom_data_recv==True and transform_rec==True):
        initial_point=False
       
        quaternion = [
          dummy.pose.pose.orientation.x,
          dummy.pose.pose.orientation.y,
          dummy.pose.pose.orientation.z,
          dummy.pose.pose.orientation.w]
        euler = tf.transformations.euler_from_quaternion(quaternion)
       # wals=tf.transformations.euler_from_quaternion(dummy.pose.pose.orientation)
        print euler
        lx2=trans[0]+dummy.pose.pose.position.x+1*np.cos(euler[2])
        ly2=trans[1]+dummy.pose.pose.position.y+1*np.sin(euler[2])
        print lx2,ly2
        cv2.line(img,(int(round(trans[0]+dummy.pose.pose.position.x)),int(round((trans[1]+dummy.pose.pose.position.y)))),(int(round(lx2)),int(round(ly2))),[0,255,0],1)
        img[int(round(trans[1]+dummy.pose.pose.position.y)),int(round(trans[0]+dummy.pose.pose.position.x)),:]=[0,0,255]
        coord_prev[0:2]=[int(round(trans[0]+dummy.pose.pose.position.x)),int(round(trans[1]+dummy.pose.pose.position.y))]
        prev_img=img.copy()
        coord_prev[2]=coord_prev[0]
        coord_prev[3]=coord_prev[1]
        all_intialisation_done=True
    if key=='x' and all_intialisation_done==True:
        img=prev_img.copy()
        coord_prev[0]=coord_prev[2]
        coord_prev[1]=coord_prev[3]
    if key=='c':
        f=createLineIterator([int(round(trans[0]+dummy.pose.pose.position.x)),int(round(trans[1]+dummy.pose.pose.position.y))],[int(round(coord_prev[0])),int(round(coord_prev[1]))], img)
        all_intialisation_done=False
        show_plot=True
    if (key == '\x03'):
        break
    if show_plot==True:
        dummy=rospy.wait_for_message('odom',Odometry)
        img[trans[1]+dummy.pose.pose.position.y,trans[0]+dummy.pose.pose.position.x,:]=[0,0,255]
    if (key == 'r'):
        initial_point=False
        odom_data_recv=False
        transform_rec=False
        show_plot=False
        img=cv2.imread("/home/rohit/scratch/src/driverless_car/maps/fivem.jpg",cv2.IMREAD_COLOR)
    cv2.imshow("waypoint_planner",img)
    cv2.waitKey(1)
   
    
        
