import sys
import tobii_research as tr
import time

eyetrackers = tr.find_all_eyetrackers()
if len(eyetrackers) >= 1 :
     eyetracker = eyetrackers[0]
else:
    print ("Error: Not Found EyeTracker")
    sys.exit()

def MyCallBack(gaze_data):
    time_stamp = gaze_data.device_time_stamp
    left_point = gaze_data.left_eye.gaze_point.position_on_display_area
    right_point = gaze_data.right_eye.gaze_point.position_on_display_area
    print ("Time:" + str(time_stamp))
    print ("Left Eye:" + str(left_point[0]) + " " + str(left_point[1]))
    print ("Right Eye:" + str(right_point[0]) + " " + str(right_point[1]))
eyetracker.subscribe_to(tr.EYETRACKER_GAZE_DATA, MyCallBack, as_dictionary=False)

time.sleep(5)
eyetracker.unsubscribe_from(tr.EYETRACKER_GAZE_DATA, MyCallBack)
