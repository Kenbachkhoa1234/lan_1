import threading
import time
import random
from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO

# Buffer với kích thước cố định
BUFFER_SIZE = 5
buffer = []

# Giới hạn số lượng sản phẩm
MAX_ITEMS = 4
produced_items = 0

# Tạo monitor với Mutex (Lock) và Condition Variable
buffer_lock = threading.Lock()
not_full = threading.Condition(buffer_lock)
not_empty = threading.Condition(buffer_lock)

from flask import Flask
from flask_cors import CORS
 # Cho phép tất cả các nguồn truy cập

# Cài đặt Flask và SocketIO
app = Flask(__name__)
socketio = SocketIO(app, threaded=True)

CORS(app, resources={r"/*": {"origins": "https://btaplon-zwj7.vercel.app"}})
products = ["Bánh", "Kẹo", "Nước", "Trà"]
# Producer class
class Producer(threading.Thread):
    def run(self):
        global buffer, produced_items
        while produced_items < MAX_ITEMS:
            item = random.choice(products)  # Sản xuất một item ngẫu nhiên
            with not_full:
                while len(buffer) == BUFFER_SIZE:
                    print("Buffer đầy, Producer đang chờ...")
                    not_full.wait()  # Chờ cho đến khi có chỗ trống trong buffer
                buffer.append(item)
                produced_items += 1
                print(f"\nProducer sản xuất : {item}. \nBuffer hiện tại: {buffer}")
                socketio.emit('update', {'type': 'produced', 'item': item, 'buffer': buffer})

            time.sleep(random.uniform(0.5, 1.5))  # Mô phỏng thời gian sản xuất

# Consumer class
class Consumer(threading.Thread):
    def run(self):
        global buffer
        while produced_items < MAX_ITEMS:
            with not_empty:
                while len(buffer) == 0:
                    print("Buffer trống, Consumer đang chờ...")
                    not_empty.wait()  # Chờ cho đến khi có item trong buffer
                item = buffer.pop(0)  # Lấy item ra khỏi buffer
                print(f"\nConsumer tiêu thụ : {item}. \nBuffer hiện tại: {buffer}")
                socketio.emit('update', {'type': 'consumed', 'item': item, 'buffer': buffer})

            time.sleep(random.uniform(1, 2))  # Mô phỏng thời gian tiêu thụ

# Route chính hiển thị giao diện web
@app.route('/')
def index():
    return render_template('index.html')

# Khởi chạy tiến trình Producer và Consumer
@app.route('/start')
def start_threads():
    producer_thread = Producer()
    consumer_thread = Consumer()

    producer_thread.start()
    consumer_thread.start()

    # Đảm bảo các thread đã kết thúc trước khi trả về kết quả
    producer_thread.join()
    consumer_thread.join()

    return jsonify({"status": "completed", "produced_items": produced_items})

if __name__ == '__main__':
    socketio.run(app, debug=True)
