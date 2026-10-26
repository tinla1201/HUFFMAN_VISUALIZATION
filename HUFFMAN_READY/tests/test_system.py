import io
import json
import os
from pathlib import Path
import random
import struct
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'backend'))
from codec import analyze, tree, compress, decompress, summary, HEADER, ENTRY, CORE, MAX_SIZE
from app import app

class CoreTests(unittest.TestCase):
    def test_banana_exact(self):
        d=analyze(b'BANANA')
        self.assertEqual(d['codes'], [{'symbol':65,'bits':'0'},{'symbol':66,'bits':'10'},{'symbol':78,'bits':'11'}])
        self.assertEqual((d['root'],d['original_size'],d['encoded_bits']),(257,6,9))
        self.assertEqual(d['steps'],[
            {'step':1,'left':66,'right':78,'parent':256,'queue_after':[65,256]},
            {'step':2,'left':65,'right':256,'parent':257,'queue_after':[257]}])
        self.assertEqual(tree(d['frequencies']),d)

    def test_empty_single(self):
        d=analyze(b'');self.assertIsNone(d['root']);self.assertEqual(d['steps'],[])
        for raw in (b'\x00'*13,b'\xff'*9):
            d=analyze(raw);self.assertEqual(d['encoded_bits'],len(raw));self.assertEqual(d['codes'][0]['bits'],'0')

    def test_all_bytes(self):
        d=analyze(bytes(range(256)))
        self.assertEqual(len(d['nodes']),511);self.assertEqual(len(d['steps']),255)
        self.assertEqual(d['encoded_bits'],2048);self.assertTrue(all(len(c['bits'])==8 for c in d['codes']))

    def test_ties_prefix_weights(self):
        raw=bytes(range(50))*3; d=analyze(raw); self.assertEqual(d,analyze(raw))
        codes=[c['bits'] for c in d['codes']]
        self.assertTrue(all(not b.startswith(a) for a in codes for b in codes if a!=b))
        nodes={n['id']:n for n in d['nodes']}
        for n in d['nodes']:
            if n['symbol'] is None:self.assertEqual(n['freq'],nodes[n['left']]['freq']+nodes[n['right']]['freq'])
        q=sorted((n['id'] for n in d['nodes'] if n['symbol'] is not None),key=lambda i:(nodes[i]['freq'],i))
        for s in d['steps']:
            self.assertEqual(q[:2],[s['left'],s['right']]);q=q[2:]+[s['parent']]
            q.sort(key=lambda i:(nodes[i]['freq'],i));self.assertEqual(q,s['queue_after'])

    def test_long_codes(self):
        freq=[0]*256; a,b=1,1
        for i in range(20):freq[i]=a;a,b=b,a+b
        d=tree(freq); self.assertGreater(max(len(c['bits']) for c in d['codes']),8)

    def test_invalid_frequency_tables(self):
        inputs=['0 '*255,'0 '*257,'-0 '+'0 '*255,'+0 '+'0 '*255,
                '0.1 '+'0 '*255,'18446744073709551616 '+'0 '*255,
                '18446744073709551615 1 '+'0 '*254,
                '16777217 '+'0 '*255,'0 '*256+'junk']
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'freq.txt'
            for data in inputs:
                with self.subTest(data=data[:30]):
                    p.write_text(data)
                    r=subprocess.run([str(CORE),'tree',str(p)],capture_output=True)
                    self.assertNotEqual(r.returncode,0);self.assertEqual(r.stdout,b'')

    def test_cli_errors(self):
        for args in ([],['bad','x'],['analyze','file-that-does-not-exist']):
            r=subprocess.run([str(CORE),*args],capture_output=True)
            self.assertNotEqual(r.returncode,0);self.assertEqual(r.stdout,b'')

    def test_limit(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'large'
            with p.open('wb') as f:f.truncate(MAX_SIZE+1)
            r=subprocess.run([str(CORE),'analyze',str(p)],capture_output=True)
            self.assertNotEqual(r.returncode,0);self.assertEqual(r.stdout,b'')
        d=tree([MAX_SIZE]+[0]*255);self.assertEqual(d['encoded_bits'],MAX_SIZE)

class CodecTests(unittest.TestCase):
    def test_roundtrip(self):
        rng=random.Random(714)
        samples=[b'',b'BANANA',b'\0'*1000,b'\xff'*17,bytes(range(256))*4,
                 'Tiếng Việt: Tín và Kiệt 🧠'.encode(),bytes(rng.randrange(256) for _ in range(100000))]
        for raw in samples:
            with self.subTest(size=len(raw)):
                blob=compress(raw);self.assertEqual(decompress(blob),raw)
                self.assertEqual(len(blob),summary(raw,analyze(raw))['stats']['compressed_bytes'])

    def test_reference_bytes(self):
        blob=compress(b'BANANA');self.assertEqual(len(blob),56);self.assertEqual(blob[-2:],b'\x9b\x00')
        self.assertEqual(len(compress(b'')),27)

    def test_fresh_process(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'test.huff';p.write_bytes(compress(b'BANANA'))
            r=subprocess.run([sys.executable,'-c',
                'from codec import decompress;import pathlib,sys;sys.stdout.buffer.write(decompress(pathlib.Path(sys.argv[1]).read_bytes()))',str(p)],
                cwd=ROOT/'backend',capture_output=True,check=True)
            self.assertEqual(r.stdout,b'BANANA')

    def test_truncated_extra_bad_magic(self):
        blob=compress(b'BANANA')
        cases=[blob[:i] for i in range(len(blob))]+[blob+b'\0',b'NOPE'+blob[4:]]
        for bad in cases:
            with self.assertRaises(ValueError):decompress(bad)

    def test_corruption(self):
        blob=compress(b'BANANA')
        # version, CRC, count table, encoded bit length, padding, payload
        for pos,mask in [(4,1),(21,1),(28,1),(13,1),(55,1),(54,128)]:
            bad=bytearray(blob);bad[pos]^=mask
            with self.subTest(pos=pos),self.assertRaises(ValueError):decompress(bytes(bad))

    def test_duplicate_symbol_and_large_size(self):
        blob=bytearray(compress(b'BANANA'));blob[36]=blob[27]
        with self.assertRaises(ValueError):decompress(bytes(blob))
        blob=bytearray(compress(b'A'));struct.pack_into('<Q',blob,5,MAX_SIZE+1)
        with self.assertRaises(ValueError):decompress(bytes(blob))

    def test_single_nonzero_bits(self):
        blob=bytearray(compress(b'A'*8));blob[-1]=128
        with self.assertRaises(ValueError):decompress(bytes(blob))

class ApiTests(unittest.TestCase):
    def setUp(self):self.client=app.test_client()
    def test_health_and_static(self):
        self.assertEqual(self.client.get('/api/health').json['status'],'ok')
        response=self.client.get('/');self.assertEqual(response.status_code,200);response.close()
    def test_json_and_file_analyze(self):
        a=self.client.post('/api/analyze',json={'text':'BANANA'})
        b=self.client.post('/api/analyze',data={'file':(io.BytesIO(b'BANANA'),'b.txt')})
        self.assertEqual(a.status_code,200);self.assertEqual(a.json['codes'],b.json['codes'])
    def test_preview_utf8(self):
        r=self.client.post('/api/preview',json={'text':'á'})
        self.assertEqual(r.json['preview_bytes'],[195,161])
    def test_http_roundtrip(self):
        raw='Xin chào Việt Nam'.encode()
        response=self.client.post('/api/compress',data={'file':(io.BytesIO(raw),'hello.txt')})
        self.assertEqual(response.status_code,200)
        d=self.client.post('/api/decompress',data={'file':(io.BytesIO(response.data),'x.huff'),'output_name':'hello.txt'})
        self.assertEqual(d.status_code,200);self.assertEqual(d.data,raw)
    def test_errors_are_json(self):
        for url,kwargs in [('/api/analyze',{'json':{'text':3}}),('/api/analyze',{}),
                           ('/api/decompress',{'data':{'file':(io.BytesIO(b'broken'),'bad.huff')}}),
                           ('/api/preview',{'data':'bad','content_type':'application/json'})]:
            r=self.client.post(url,**kwargs);self.assertEqual(r.status_code,400);self.assertIn('error',r.json)
        r=self.client.get('/api/missing');self.assertEqual(r.status_code,404);self.assertTrue(r.is_json)
    def test_missing_core(self):
        from unittest.mock import patch
        with patch('codec.CORE',Path('/not-installed/huffman_core')):
            r=self.client.post('/api/analyze',json={'text':'A'})
            self.assertEqual(r.status_code,503);self.assertIn('error',r.json)

if __name__=='__main__':unittest.main(verbosity=2)
