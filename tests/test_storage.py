"""storage 层测试：文件读写、白名单、流水线落盘。"""
import os
import tempfile
import unittest

from tutorfilter import storage


class StorageTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = self.tmp.name
        for name, text in [
            ("Blocked_words.txt", "英语\n"),
            ("Personal_info.txt", "地址：霞山\n科目：数学\n"),
            ("Tutor_info.txt", "【地址】霞山\n【科目】数学\n\n【地址】赤坎\n【科目】英语\n"),
        ]:
            with open(os.path.join(self.dir, name), "w", encoding="utf-8") as f:
                f.write(text)

    def tearDown(self):
        self.tmp.cleanup()

    def test_run_writes_res_txt(self):
        result = storage.run(self.dir)
        self.assertEqual((result.total, result.filtered_out, result.kept), (2, 1, 1))
        with open(os.path.join(self.dir, "res.txt"), encoding="utf-8") as f:
            self.assertEqual(f.read(), "===== 第 1 个 =====\n【地址】霞山\n【科目】数学\n\n")

    def test_missing_input_names_the_file(self):
        os.remove(os.path.join(self.dir, "Tutor_info.txt"))
        with self.assertRaises(FileNotFoundError) as ctx:
            storage.run(self.dir)
        self.assertIn("Tutor_info.txt", str(ctx.exception))

    def test_filename_whitelist_blocks_traversal(self):
        with self.assertRaises(ValueError):
            storage.read_file(self.dir, "../teach.py")
        with self.assertRaises(ValueError):
            storage.append_file(self.dir, "C:/Windows/win.ini", "x")

    def test_reset_and_append_roundtrip(self):
        storage.reset_file(self.dir, "Blocked_words.txt")
        self.assertEqual(storage.read_file(self.dir, "Blocked_words.txt"), "")
        storage.append_file(self.dir, "Blocked_words.txt", "语文、物理\n")
        self.assertEqual(storage.read_file(self.dir, "Blocked_words.txt"), "语文、物理\n")

    def test_default_data_dir_points_at_project_data(self):
        self.assertTrue(storage.default_data_dir().endswith("data"))


if __name__ == "__main__":
    unittest.main()
