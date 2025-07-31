import cv2
import datetime
import subprocess
import time

# 解像度・FPS設定
WIDTH, HEIGHT = 1280, 720
CAMERA_ID = 0
TARGET_FPS = 10

# カメラ初期化
cap = cv2.VideoCapture(CAMERA_ID)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)
cap.set(cv2.CAP_PROP_FPS, TARGET_FPS)
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))  # MJPEG圧縮有効

# FFmpegコマンド（高速化＋低レイテンシ最適化）
ffmpeg_cmd = [
    'ffmpeg',
    '-y',
    '-f', 'rawvideo',
    '-pix_fmt', 'bgr24',
    '-s', f'{WIDTH}x{HEIGHT}',
    '-r', str(TARGET_FPS),
    '-i', '-',
    '-vcodec', 'libx264',
    '-preset', 'ultrafast',
    '-tune', 'zerolatency',
    '-threads', '2',
    '-fps_mode', 'passthrough',
    '-g', '10',
    '-keyint_min', '10',
    '-analyzeduration', '0',
    '-fflags', 'nobuffer',
    '-f', 'rtsp',
    'rtsp://100.101.30.82:8555/live.stream'
]

# FFmpeg起動
process = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE)

while True:
    start = time.time()

    ret, frame = cap.read()
    if not ret:
        print("フレームの取得に失敗しました")
        break

    # 日時文字列生成
    now_text = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale = 1.5
    color = (0, 255, 0)
    thickness = 3

    (text_w, text_h), _ = cv2.getTextSize(now_text, font, font_scale, thickness)
    x = frame.shape[1] - text_w - 10
    y = frame.shape[0] - 10
    cv2.putText(frame, now_text, (x, y), font, font_scale, color, thickness)

    # FFmpegに送信
    process.stdin.write(frame.tobytes())

    # FPS調整
    elapsed = time.time() - start
    sleep = max(0, (1.0 / TARGET_FPS) - elapsed)
    time.sleep(sleep)

# 後処理
cap.release()
process.stdin.close()
process.wait()
