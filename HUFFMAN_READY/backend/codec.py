"""HUF1 container. Huffman tree construction remains exclusively in C."""
from pathlib import Path
from collections import Counter
import json
import os
import struct
import subprocess
import tempfile
import zlib

MAX_SIZE = 16 * 1024 * 1024
CORE = Path(__file__).resolve().parents[1] / 'core' / ('huffman_core.exe' if os.name == 'nt' else 'huffman_core')
HEADER = struct.Struct('<4sBQQIH')
ENTRY = struct.Struct('<BQ')

class CoreError(RuntimeError):
    pass


def call_core(mode, content):
    if not CORE.is_file():
        raise CoreError('Chưa có lõi C. Chạy python build_core.py tại thư mục gốc dự án.')
    try:
        with tempfile.TemporaryDirectory(prefix='huffman_') as temp:
            path = Path(temp) / 'input.bin'
            path.write_bytes(content)
            proc = subprocess.run([str(CORE), mode, str(path)], check=True,
                                  capture_output=True, text=True, encoding='utf-8', timeout=30)
        result = json.loads(proc.stdout)
        if result.get('schema_version') != 1:
            raise CoreError('Lõi C không đúng schema V1.')
        return result
    except subprocess.CalledProcessError as exc:
        raise CoreError('Lõi C báo lỗi: ' + exc.stderr.strip()) from exc
    except (OSError, subprocess.TimeoutExpired, UnicodeError, json.JSONDecodeError) as exc:
        raise CoreError('Không chạy/đọc được lõi C: ' + str(exc)) from exc


def analyze(raw):
    if len(raw) > MAX_SIZE:
        raise ValueError('Dữ liệu vượt giới hạn 16 MiB.')
    return call_core('analyze', raw)


def tree(freq):
    return call_core('tree', ' '.join(map(str, freq)).encode('ascii'))


def summary(raw, model):
    bits = model['encoded_bits']
    k = len(model['codes'])
    payload = (bits + 7) // 8
    overhead = HEADER.size + ENTRY.size * k
    size = len(raw)
    code_map = {row['symbol']: row['bits'] for row in model['codes']}
    # Bounded preview, never allocate the complete bit string.
    preview = ''.join(code_map[b] for b in raw[:256])[:256]
    return {**model, 'preview_bytes': list(raw[:64]), 'truncated': size > 64,
            'encoded_preview': preview, 'encoded_preview_truncated': bits > len(preview),
            'stats': {'original_bytes': size, 'encoded_bits': bits,
                      'padding_bits': (-bits) % 8, 'payload_bytes': payload,
                      'header_bytes': overhead, 'compressed_bytes': overhead + payload,
                      'average_bits': bits / size if size else None,
                      'saving_percent': 100 * (1 - (overhead + payload) / size) if size else None}}


def compress(raw):
    model = analyze(raw)
    code_map = {x['symbol']: (int(x['bits'], 2), len(x['bits'])) for x in model['codes']}
    payload = bytearray()
    acc = count = 0
    for symbol in raw:
        value, length = code_map[symbol]
        acc = (acc << length) | value
        count += length
        while count >= 8:
            count -= 8
            payload.append((acc >> count) & 255)
        acc &= (1 << count) - 1
    if count:
        payload.append(acc << (8 - count))
    entries = [(i, f) for i, f in enumerate(model['frequencies']) if f]
    header = HEADER.pack(b'HUF1', 1, len(raw), model['encoded_bits'], zlib.crc32(raw) & 0xffffffff, len(entries))
    return header + b''.join(ENTRY.pack(*entry) for entry in entries) + bytes(payload)


def decompress(blob):
    if len(blob) < HEADER.size:
        raise ValueError('Tập tin bị cắt ngắn: thiếu header.')
    magic, version, size, bits, crc, k = HEADER.unpack_from(blob)
    if magic != b'HUF1' or version != 1:
        raise ValueError('Không phải tập tin HUF1 phiên bản 1.')
    if size > MAX_SIZE or k > 256 or bits > size * 255:
        raise ValueError('Thông tin kích thước không hợp lệ.')
    offset = HEADER.size + k * ENTRY.size
    if len(blob) != offset + (bits + 7) // 8:
        raise ValueError('Tập tin thiếu hoặc thừa byte so với header.')
    freq = [0] * 256
    previous = -1
    for i in range(k):
        symbol, count = ENTRY.unpack_from(blob, HEADER.size + i * ENTRY.size)
        if symbol <= previous or not count or count > MAX_SIZE:
            raise ValueError('Bảng tần suất không hợp lệ.')
        previous = symbol
        freq[symbol] = count
    if sum(freq) != size:
        raise ValueError('Tổng tần suất không bằng kích thước gốc.')
    model = tree(freq)
    if model['encoded_bits'] != bits:
        raise ValueError('Số bit không khớp cây Huffman.')
    payload = blob[offset:]
    padding = (-bits) % 8
    if padding and payload[-1] & ((1 << padding) - 1):
        raise ValueError('Bit đệm phải bằng 0.')
    if k == 0:
        output = b''
    elif k == 1:
        if any(payload):
            raise ValueError('Mã của tập tin một ký hiệu phải toàn bit 0.')
        output = bytes([previous]) * size
    else:
        nodes = {n['id']: n for n in model['nodes']}
        root = model['root']
        current = root
        output = bytearray()
        for i in range(bits):
            bit = (payload[i // 8] >> (7 - i % 8)) & 1
            current = nodes[current]['right' if bit else 'left']
            node = nodes[current]
            if node['symbol'] is not None:
                output.append(node['symbol'])
                if len(output) > size:
                    raise ValueError('Giải mã vượt kích thước khai báo.')
                current = root
        if current != root:
            raise ValueError('Dữ liệu kết thúc giữa một mã Huffman.')
        output = bytes(output)
    if len(output) != size:
        raise ValueError('Kích thước dữ liệu khôi phục không đúng.')
    actual = Counter(output)
    if any(actual[i] != freq[i] for i in range(256)):
        raise ValueError('Tần suất khôi phục không khớp header.')
    if zlib.crc32(output) & 0xffffffff != crc:
        raise ValueError('CRC không khớp: tập tin đã bị thay đổi hoặc hỏng.')
    return output
