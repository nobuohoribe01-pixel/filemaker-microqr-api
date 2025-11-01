from flask import Flask, request, send_file
import segno
from io import BytesIO

app = Flask(__name__)

@app.route('/microqr')  #  <-- /api/ は不要になった
def generate_micro_qr():
    data_to_encode = request.args.get('data', '')
    if not data_to_encode:
        return "Data parameter is missing.", 400
    try:
        qrcode = segno.make(data_to_encode, micro=True, error='m')
        buffer = BytesIO()
        qrcode.save(buffer, kind='png', scale=10, border=1)
        buffer.seek(0)
        return send_file(buffer, mimetype='image/png')
    except Exception as e:
        return f"Error: {e}", 500
```    *   **変更点:** 7行目の `@app.route()` の中から `/api` を削除し、`/microqr` だけにしました。
