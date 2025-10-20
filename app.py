from flask import Flask, jsonify, render_template
import tobii_research as tr
import threading, math, csv, time, os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ========= 視線データ関連 =========
gaze_data = {'x': 0, 'y': 0}
last_gaze_data = {'x': 0, 'y': 0}
distance_travelled = 0

found_eyetrackers = tr.find_all_eyetrackers()
eyetracker = found_eyetrackers[0] if found_eyetrackers else None

def gaze_data_callback(gaze_data_response):
    global gaze_data, last_gaze_data, distance_travelled
    if gaze_data_response['left_gaze_point_validity'] and gaze_data_response['right_gaze_point_validity']:
        gaze_data['x'] = (gaze_data_response['left_gaze_point_on_display_area'][0] +
                          gaze_data_response['right_gaze_point_on_display_area'][0]) / 2
        gaze_data['y'] = (gaze_data_response['left_gaze_point_on_display_area'][1] +
                          gaze_data_response['right_gaze_point_on_display_area'][1]) / 2
        distance = math.sqrt((gaze_data['x'] - last_gaze_data['x'])**2 + (gaze_data['y'] - last_gaze_data['y'])**2)
        distance_travelled += distance
        last_gaze_data.update(gaze_data)
        save_gaze_data_to_csv(gaze_data)

def save_gaze_data_to_csv(data):
    with open('gaze_data.csv', 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([time.time(), data['x'], data['y']])

@app.route('/gaze_data')
def get_gaze_data():
    return jsonify(gaze_data)

# ========= 読書データAPI =========
BASE_PATH = "data/files/text"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/authors')
def get_authors():
    authors = [a for a in os.listdir(BASE_PATH) if os.path.isdir(os.path.join(BASE_PATH, a))]
    return jsonify(authors)

@app.route('/api/works/<author>')
def get_works(author):
    folder = os.path.join(BASE_PATH, author)
    works = [os.path.splitext(f)[0] for f in os.listdir(folder) if f.endswith('.html')]
    return jsonify(works)

@app.route('/api/work/<author>/<title>')
def get_work(author, title):
    path = os.path.join(BASE_PATH, author, f"{title}.html")
    try:
        with open(path, encoding='utf-8') as f:
            content = f.read()
        return jsonify({'author': author, 'title': title, 'content': content})
    except FileNotFoundError:
        return jsonify({'error': 'not found'}), 404

if __name__ == '__main__':
    if eyetracker:
        t = threading.Thread(target=lambda: eyetracker.subscribe_to(tr.EYETRACKER_GAZE_DATA, gaze_data_callback, as_dictionary=True))
        t.daemon = True
        t.start()
    app.run(debug=True, port=5001)
