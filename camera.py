from flask import Flask, Response
import cv2

app = Flask(__name__)

# USBカメラ（/dev/video0）を初期化
camera = cv2.VideoCapture("/dev/video0")
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

def generate_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break
        # JPEG形式にエンコード
        _, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()

        # MJPEGとして出力
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' +
               frame_bytes + b'\r\n')

@app.route('/')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    print("[INFO] MJPEGストリームを http://0.0.0.0:8080/ で配信中")
    app.run(host='0.0.0.0', port=8080)
