import subprocess
import json
import os
import unittest

CORE_EXEC = os.path.join(os.path.dirname(__file__), "..", "huffman_core.exe" if os.name == 'nt' else "huffman_core")

class TestHuffmanCore(unittest.TestCase):
    def run_core(self, cmd, arg):
        result = subprocess.run([CORE_EXEC, cmd, arg], capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 0, f"Core failed: {result.stderr}")
        return json.loads(result.stdout)

    def test_01_banana(self):
        with open("temp_banana.txt", "wb") as f: f.write(b"BANANA")
        data = self.run_core("analyze", "temp_banana.txt")
        self.assertEqual(data["original_size"], 6)
        self.assertEqual(data["encoded_bits"], 9)
        self.assertEqual(data["root"], 257)
        self.assertEqual(data["frequencies"][65], 3)
        self.assertEqual(data["frequencies"][66], 1)
        self.assertEqual(data["frequencies"][78], 2)
        os.remove("temp_banana.txt")

    def test_02_empty(self):
        with open("temp_empty.txt", "wb") as f: pass
        data = self.run_core("analyze", "temp_empty.txt")
        self.assertEqual(data["original_size"], 0)
        self.assertIsNone(data["root"])
        self.assertEqual(len(data["nodes"]), 0)
        os.remove("temp_empty.txt")

    def test_03_one_byte_loop(self):
        with open("temp_one.txt", "wb") as f: f.write(b"\x00" * 10)
        data = self.run_core("analyze", "temp_one.txt")
        self.assertEqual(data["original_size"], 10)
        self.assertEqual(data["encoded_bits"], 10)
        self.assertEqual(data["codes"][0]["bits"], "0")
        os.remove("temp_one.txt")

    def test_04_tree_command_sync(self):
        with open("temp_banana.txt", "wb") as f: f.write(b"BANANA")
        analyze_data = self.run_core("analyze", "temp_banana.txt")
        
        with open("temp_freq.txt", "w") as f:
            f.write(" ".join(map(str, analyze_data["frequencies"])))
        
        tree_data = self.run_core("tree", "temp_freq.txt")
        self.assertEqual(analyze_data, tree_data)
        
        os.remove("temp_banana.txt")
        os.remove("temp_freq.txt")

    def test_05_file_not_found(self):
        result = subprocess.run([CORE_EXEC, "analyze", "non_existent.txt"], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Cannot open input file", result.stderr)

if __name__ == '__main__':
    unittest.main()
