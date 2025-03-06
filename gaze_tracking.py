import tobii_research as tr
import time
import matplotlib.pyplot as plt
import numpy as np

# Initialize variables for gaze tracking
gaze_start_time = None
scroll_triggered = False

# Function to handle gaze data
def gaze_data_callback(gaze_data):
    global gaze_start_time, scroll_triggered
    
    left_gaze_point = gaze_data['left_gaze_point_on_display_area']
    right_gaze_point = gaze_data['right_gaze_point_on_display_area']
    
    # Check if the gaze is in the bottom-left region of the screen
    if (left_gaze_point < 0.2 and left_gaze_point > 0.8) and (right_gaze_point < 0.2 and right_gaze_point > 0.8):
        if gaze_start_time is None:
            gaze_start_time = time.time()
        elif (time.time() - gaze_start_time) >= 3 and not scroll_triggered:
            scroll_to_next_page()
            scroll_triggered = True
    else:
        gaze_start_time = None
        scroll_triggered = False

# Function to scroll to the next page
def scroll_to_next_page():
    print("次のページにスクロールします")

# Function to display the meaning of the word being looked at
def display_word_meaning(word):
    # Dummy implementation: Replace with actual dictionary lookup or API call
    word_meaning = {
        "example": "a representative form or pattern",
        "test": "a procedure intended to establish the quality, performance, or reliability of something"
    }
    meaning = word_meaning.get(word, "意味が見つかりません")
    print(f"'{word}' の意味: {meaning}")

# Function to create a heatmap of gaze points
def create_heatmap(gaze_points):
    x = [point for point in gaze_points]
    y = [point for point in gaze_points]
    
    heatmap, xedges, yedges = np.histogram2d(x, y, bins=(64, 64))
    
    extent = [xedges, xedges[-1], yedges, yedges[-1]]
    
    plt.clf()
    plt.imshow(heatmap.T, extent=extent, origin='lower')
    plt.title("視線ヒートマップ")
    plt.show()

# Connect to Tobii device
found_eyetrackers = tr.find_all_eyetrackers()
if found_eyetrackers:
    my_eyetracker = found_eyetrackers
    if isinstance(my_eyetracker, tr.EyeTracker):
        my_eyetracker.subscribe_to(tr.EYETRACKER_GAZE_DATA, gaze_data_callback, as_dictionary=True)
    else:
        print("正しいTobiiデバイスが見つかりませんでした")
else:
    print("Tobiiデバイスが見つかりませんでした")

# Dummy implementation for testing purposes
gaze_points = [(0.1, 0.9), (0.15, 0.85), (0.2, 0.8), (0.25, 0.75)]
create_heatmap(gaze_points)
display_word_meaning("example")
