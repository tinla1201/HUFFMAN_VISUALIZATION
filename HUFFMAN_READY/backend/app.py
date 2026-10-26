from io import BytesIO
from pathlib import Path
from flask import Flask, jsonify, request, send_file, send_from_directory
from werkzeug.exceptions import HTTPException
from werkzeug.utils import secure_filename
from codec import MAX_SIZE, CoreError, analyze, summary, compress, decompress

DIST = Path(__file__).resolve().parents[1] / 'frontend' / 'dist'
app = Flask(__name__, static_folder=None)
# Full multipart/JSON request limit; the raw-data limit is checked separately.
app.config['MAX_CONTENT_LENGTH'] = 112 * 1024 * 1024

@app.errorhandler(HTTPException)
def http_error(exc):
    return jsonify(error=exc.description), exc.code

@app.errorhandler(ValueError)
def value_error(exc):
    return jsonify(error=str(exc)), 400

@app.errorhandler(CoreError)
def core_error(exc):
    return jsonify(error=str(exc)), 503


def source():
    if request.is_json:
        data = request.get_json(silent=True)
        if not isinstance(data, dict) or not isinstance(data.get('text'), str):
            raise ValueError('Trường text phải là chuỗi văn bản.')
        raw = data['text'].encode('utf-8')
        name = 'vanban.txt'
    else:
        uploaded = request.files.get('file')
        if uploaded is None or not uploaded.filename:
            raise ValueError('Bạn chưa chọn tập tin.')
        raw = uploaded.stream.read(MAX_SIZE + 1)
        name = uploaded.filename.replace('\\', '/').split('/')[-1]
    if len(raw) > MAX_SIZE:
        raise ValueError('Dữ liệu vượt giới hạn 16 MiB.')
    return raw, name

@app.get('/api/health')
def health():
    return jsonify(status='ok', message='Huffman backend is running', schema_version=1)

@app.post('/api/preview')
@app.post('/api/preview-file')
def preview():
    raw, name = source()
    return jsonify(schema_version=1, filename=name, original_size=len(raw),
                   preview_bytes=list(raw[:64]), truncated=len(raw)>64)

@app.post('/api/analyze')
def analyze_route():
    raw, name = source()
    return jsonify(**summary(raw, analyze(raw)), filename=name)

@app.post('/api/compress')
def compress_route():
    raw, name = source()
    blob = compress(raw)
    return send_file(BytesIO(blob), mimetype='application/octet-stream', as_attachment=True,
                     download_name=(secure_filename(name) or 'data') + '.huff')

@app.post('/api/decompress')
def decompress_route():
    uploaded = request.files.get('file')
    if uploaded is None or not uploaded.filename:
        raise ValueError('Hãy chọn tập tin .huff.')
    # Optimal Huffman cannot exceed the valid fixed 8-bit code for k>=2.
    blob = uploaded.stream.read(MAX_SIZE + 27 + 9*256 + 1)
    if len(blob) > MAX_SIZE + 27 + 9*256:
        raise ValueError('Tập tin nén vượt giới hạn V1.')
    raw = decompress(blob)
    filename = secure_filename(request.form.get('output_name', 'khoi-phuc.bin')) or 'khoi-phuc.bin'
    return send_file(BytesIO(raw), mimetype='application/octet-stream', as_attachment=True, download_name=filename)

@app.get('/')
def home():
    if (DIST / 'index.html').is_file():
        return send_from_directory(DIST, 'index.html')
    return 'Backend đang chạy. Mở React ở http://127.0.0.1:5173 hoặc build frontend.'

@app.get('/assets/<path:name>')
def assets(name):
    return send_from_directory(DIST / 'assets', name)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=False)
