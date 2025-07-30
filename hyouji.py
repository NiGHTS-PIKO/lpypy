#!/usr/bin/env python3
from flask import Flask, jsonify
import psutil
import subprocess
import datetime

app = Flask(__name__)

def get_cpu_temp():
    try:
        result = subprocess.run(
            ['vcgencmd', 'measure_temp'], 
            capture_output=True, text=True
        )
        temp_str = result.stdout.strip().replace("temp=", "").replace("'C", "")
        return float(temp_str)
    except Exception:
        return None

def get_system_data():
    cpu_percent = psutil.cpu_percent(interval=1)
    temp = get_cpu_temp()
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return {
        'cpu_percent': cpu_percent,
        'temperature': temp,
        'timestamp': timestamp
    }

@app.route('/')
def index():
    return '''
        <html>
            <head><title>Raspberry Pi モニタ</title></head>
            <body style="font-family: Arial; text-align: center; margin-top: 50px;">
                <h1>リアルタイムシステム表示</h1>
                <div id="data" style="font-size: 3.5em;"></div>
                <script>
                    async function fetchData() {
                        const res = await fetch('/data');
                        const json = await res.json();
                        document.getElementById("data").innerHTML =
                            `<p><strong>CPU使用率:</strong> ${json.cpu_percent}%</p>
                             <p><strong>CPU温度:</strong> ${json.temperature ?? "N/A"}℃</p>
                             <p><strong>取得時刻:</strong> ${json.timestamp}</p>`;
                    }
                    setInterval(fetchData, 2980);
                    fetchData();
                </script>
            </body>
        </html>
    '''

@app.route('/data')
def data():
    return jsonify(get_system_data())

if __name__ == '__main__':
    app.run(host='0.0.0.0')
