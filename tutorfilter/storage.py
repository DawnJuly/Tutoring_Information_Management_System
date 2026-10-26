"""数据文件读写。文件名白名单杜绝路径穿越；缺文件抛带文件名的 FileNotFoundError。"""
import os

from tutorfilter import core

DATA_FILES = ("Blocked_words.txt", "Personal_info.txt", "Tutor_info.txt", "res.txt")
INPUT_FILES = DATA_FILES[:3]


def default_data_dir():
    return os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")


def _path(data_dir, name):
    if name not in DATA_FILES:
        raise ValueError(f"非法文件名：{name}（可用：{'、'.join(DATA_FILES)}）")
    return os.path.join(data_dir, name)


def _read(data_dir, name):
    with open(_path(data_dir, name), "r", encoding="utf-8") as f:
        return f.read()


def read_file(data_dir, name):
    return _read(data_dir, name)


def reset_file(data_dir, name):
    with open(_path(data_dir, name), "w", encoding="utf-8") as f:
        f.write("")


def append_file(data_dir, name, content):
    with open(_path(data_dir, name), "a", encoding="utf-8") as f:
        f.write(content)


def run(data_dir):
    """跑流水线并写 res.txt，返回 core.RunResult。"""
    texts = []
    for name in INPUT_FILES:
        try:
            texts.append(_read(data_dir, name))
        except FileNotFoundError:
            raise FileNotFoundError(f"未找到数据文件：{os.path.join(data_dir, name)}") from None
    result = core.run(*texts)
    with open(_path(data_dir, "res.txt"), "w", encoding="utf-8") as f:
        f.write(core.format_result(result.results))
    return result
