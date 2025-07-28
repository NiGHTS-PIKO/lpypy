import socket
import threading

DEFAULT_HOST = 'atomcam.local'
DEFAULT_PORT = 8554
LISTEN_PORT = 8554

class ProxyServer:
    def __init__(self, host):
        self.host = host
        self.running = False
        self.server_socket = None
        self.threads = []
        self.connections = []

    def start(self):
        self.running = True
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(('0.0.0.0', LISTEN_PORT))
        self.server_socket.listen(5)
        threading.Thread(target=self.accept_loop, daemon=True).start()
        print(f"[INFO] Proxy起動 (Port {LISTEN_PORT})")

    def accept_loop(self):
        while self.running:
            try:
                client, _ = self.server_socket.accept()
                server = socket.create_connection((self.host, DEFAULT_PORT))
                self.connections.append((client, server))
                for a, b in ((client, server), (server, client)):
                    threading.Thread(target=self.forward, args=(a, b), daemon=True).start()
            except Exception as e:
                print(f"[ERROR] accept失敗: {e}")
                break

    def forward(self, src, dst):
        try:
            while True:
                data = src.recv(4096)
                if not data: break
                dst.sendall(data)
        except: pass
        finally:
            src.close()
            dst.close()

if __name__ == "__main__":
    ProxyServer(DEFAULT_HOST).start()
    threading.Event().wait()  # 永久待機
