# tests/test_storage.py
import unittest
import tempfile
import os
import storage

class StorageTest(unittest.TestCase):
    def test_save_load_roundtrip(self):
        fd, path = tempfile.mkstemp(suffix=".json")
        os.close(fd)
        try:
            tasks = []
            tasks.append(storage.make_task("hello"))
            storage.save_tasks(tasks, path=path)
            loaded = storage.load_tasks(path=path)
            self.assertEqual(len(loaded), 1)
            self.assertEqual(loaded[0]["task"], "hello")
        finally:
            os.remove(path)

if __name__ == "__main__":
    unittest.main()