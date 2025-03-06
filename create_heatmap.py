import json
import numpy as np
import matplotlib.pyplot as plt
import math

# 視線データのファイルパス
gaze_data_file = 'gaze_data.json'

# 視線データをファイルから読み込む
with open(gaze_data_file, 'r') as file:
    gaze_data = json.load(file)

# x, y 座標のリストを取り出し
x_coords = gaze_data['x']
y_coords = gaze_data['y']

# ヒートマップのサイズ（画面の解像度に応じて調整）
heatmap_size = (800, 600)  # 幅800px, 高さ600px

# ヒートマップ用の空のグリッドを作成
heatmap = np.zeros(heatmap_size)

# 視線データをヒートマップに変換
for x, y in zip(x_coords, y_coords):
    # 座標をピクセル値に変換
    x_pixel = int(x * heatmap_size[0])
    y_pixel = int(y * heatmap_size[1])

    # 座標が範囲内にあればヒートマップに加算
    if 0 <= x_pixel < heatmap_size[0] and 0 <= y_pixel < heatmap_size[1]:
        heatmap[y_pixel, x_pixel] += 1

# ヒートマップを表示
plt.imshow(heatmap, cmap='hot', interpolation='nearest')
plt.colorbar(label="視線頻度")
plt.title("視線ヒートマップ")
plt.show()

# 視線移動距離の計算
def calculate_total_distance(x_coords, y_coords):
    total_distance = 0
    for i in range(1, len(x_coords)):
        dx = x_coords[i] - x_coords[i-1]
        dy = y_coords[i] - y_coords[i-1]
        distance = math.sqrt(dx**2 + dy**2)
        total_distance += distance
    return total_distance

# 視線移動距離を計算
total_distance = calculate_total_distance(x_coords, y_coords)

# 距離を表示（cmに変換）
print(f"視線の総移動距離: {total_distance * 100} cm")

