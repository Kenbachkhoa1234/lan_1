import threading
import time
import random
from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO
from flask_cors import CORS

# Kích thước buffer cố định
KICH_THUOC_BUFFER = 5
buffer = []

# Giới hạn số sản phẩm tối đa
SO_SAN_PHAM_TTOI_DA = 4
so_san_pham_da_san_xuat = 0

# Tạo monitor với Mutex (Lock) và Condition Variable
buffer_lock = threading.Lock()
not_full = threading.Condition(buffer_lock)
not_empty = threading.Condition(buffer_lock)

# Khởi tạo Flask và SocketIO
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Cho phép tất cả các nguồn
socketio = SocketIO(app, cors_allowed_origins='*', threaded=True)

# Danh sách sản phẩm để sản xuất
san_pham = ["bánh", "kẹo", "nước", "trà"]

# Lớp sản xuất sản phẩm
class NhaSanXuatThucTe(threading.Thread):
    def run(self):
        global buffer, so_san_pham_da_san_xuat
        while so_san_pham_da_san_xuat < SO_SAN_PHAM_TTOI_DA:
            san_pham_moi = random.choice(san_pham)
            with not_full:
                while len(buffer) == KICH_THUOC_BUFFER:
                    print("Buffer đã đầy, nhà sản xuất tạm dừng...")
                    not_full.wait()  # Chờ cho đến khi có chỗ trống
                buffer.append(san_pham_moi)
                so_san_pham_da_san_xuat += 1
                print(f"Đã sản xuất: {san_pham_moi}. Trạng thái buffer: {buffer}")
                socketio.emit('update', {'type': 'produced', 'item': san_pham_moi, 'buffer': buffer})

            time.sleep(random.uniform(0.5, 1.5))  # Thời gian sản xuất

# Lớp tiêu thụ sản phẩm
class KhachHang(threading.Thread):
    def run(self):
        global buffer
        while so_san_pham_da_san_xuat < SO_SAN_PHAM_TTOI_DA:
            with not_empty:
                while len(buffer) == 0:
                    print("Buffer trống, khách hàng chờ đợi...")
                    not_empty.wait()  # Chờ cho đến khi có sản phẩm
                san_pham_tieu_thu = buffer.pop(0)
                print(f"Khách hàng đã tiêu thụ: {san_pham_tieu_thu}. Trạng thái buffer: {buffer}")
                socketio.emit('update', {'type': 'consumed', 'item': san_pham_tieu_thu, 'buffer': buffer})

            time.sleep(random.uniform(1, 2))  # Thời gian tiêu thụ

# Route chính để hiển thị giao diện web
@app.route('/')
def index():
    return render_template('index.html')

# Khởi động các luồng sản xuất và tiêu thụ
@app.route('/start')
def start_threads():
    nha_san_xuat_thread = NhaSanXuatThucTe()
    khach_hang_thread = KhachHang()

    nha_san_xuat_thread.start()
    khach_hang_thread.start()

    # Đảm bảo các luồng đã hoàn thành
    nha_san_xuat_thread.join()
    khach_hang_thread.join()

    return jsonify({"status": "completed", "produced_items": so_san_pham_da_san_xuat})

if __name__ == '__main__':
    socketio.run(app, debug=True)
