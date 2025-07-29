from flask import Flask, Response
import cv2
import datetime

app = Flask(__name__)

camera = cv2.VideoCapture("/dev/video0")
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

def generate_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break

        # リアルタイム日時取得
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 日時の描画設定（少し小さめ & 右下）
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 1.2
        font_thickness = 2
        time_text = now
        time_size = cv2.getTextSize(time_text, font, font_scale, font_thickness)[0]

        # 右下に配置
        x = frame.shape[1] - time_size[0] - 10
        y = frame.shape[0] - 10
        cv2.putText(frame, time_text,
                    (x, y),
                    font, font_scale, (0, 255, 0), font_thickness)

        _, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

@app.route('/')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    print("[INFO] MJPEGストリーム配信中： http://0.0.0.0:8080/")
    app.run(host='0.0.0.0', port=8080)