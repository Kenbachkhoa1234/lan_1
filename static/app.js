var socket = io.connect('https://troi-oi.vercel.app/');
var socket = io();
socket.on('update', function(data) {
    var resultDiv = document.getElementById('result');
    if (data.type === 'produced') {
        resultDiv.innerHTML += `
            <p>Producer sản xuất item: ${data.item}<br>
            Buffer hiện tại: ${JSON.stringify(data.buffer)}</p>`;
    } else if (data.type === 'consumed') {
        resultDiv.innerHTML += `
            <p>Consumer tiêu thụ item: ${data.item}<br>
            Buffer hiện tại: ${JSON.stringify(data.buffer)}</p>`;
    }

    // Tự động cuộn xuống cuối nếu có nội dung mới
    resultDiv.scrollTop = resultDiv.scrollHeight;
});

function start() {
    fetch('/start')
        .then(response => response.json())
        .then(data => {
            document.getElementById('status').innerText = "Quá trình hoàn thành!";
        })
        .catch(err => {
            console.error("Đã xảy ra lỗi:", err);
            document.getElementById('status').innerText = "Có lỗi xảy ra, vui lòng thử lại.";
        });
}
