"""家教信息筛选排序系统 -- 核心算法模块

该模块不依赖 Toga，可独立运行和测试。
数据目录可通过 set_data_dir() 指定；在 Android 上由 app.py 在启动时
设置为应用私有可写目录，并将打包的默认数据复制过去。
"""
import os
import shutil

# 可写数据目录（由外部设置，默认使用脚本同级 data 目录）
_data_dir = None

# 需要管理的文件
DATA_FILES = [
    'Blocked_words.txt',
    'Personal_info.txt',
    'Tutor_info.txt',
    'res.txt',
]


def set_data_dir(path):
    """设置数据文件的读写目录"""
    global _data_dir
    _data_dir = path


def get_data_dir():
    """获取数据文件目录"""
    if _data_dir:
        return _data_dir
    # 默认：脚本所在目录下的 data 子目录
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')


def get_builtin_data_dir():
    """获取打包进应用内的只读数据目录"""
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')


def ensure_data_files():
    """确保数据文件存在（首次启动时从内置目录复制到可写目录）"""
    data_dir = get_data_dir()
    builtin_dir = get_builtin_data_dir()
    os.makedirs(data_dir, exist_ok=True)

    for fname in DATA_FILES:
        target = os.path.join(data_dir, fname)
        source = os.path.join(builtin_dir, fname)
        # 若目标不存在且源存在且路径不同，则复制
        if not os.path.exists(target) and os.path.exists(source):
            if os.path.abspath(source) != os.path.abspath(target):
                try:
                    shutil.copyfile(source, target)
                except (IOError, OSError):
                    pass
    return data_dir


def read_txt():
    """读取三个数据文件，返回 (Blocked_words, Personal_info, Tutor_info)"""
    base = ensure_data_files()

    # 读取屏蔽词文件
    try:
        with open(os.path.join(base, 'Blocked_words.txt'), 'r', encoding='utf-8') as f:
            Blocked_words = []
            for line in f.readlines():
                line = line.strip()
                if line:
                    Blocked_words.extend(line.split('、'))
    except FileNotFoundError:
        return None, None, None

    # 读取个人信息文件
    try:
        with open(os.path.join(base, 'Personal_info.txt'), 'r', encoding='utf-8') as f:
            Personal_info = {}
            for line in f.readlines():
                line = line.strip()
                if line and '：' in line:
                    parts = line.split('：')
                    Personal_info[parts[0]] = parts[-1]
    except FileNotFoundError:
        return None, None, None

    # 读取家教信息文件
    try:
        with open(os.path.join(base, 'Tutor_info.txt'), 'r', encoding='utf-8') as f:
            content = f.read()
            content = content.replace('\r\n', '\n')
            Tutor_info = [item.strip() for item in content.split('\n\n') if item.strip()]
    except FileNotFoundError:
        return None, None, None

    return Blocked_words, Personal_info, Tutor_info


def filter_tutors(Blocked_words, Tutor_info):
    """遍历筛选：移除包含任意屏蔽词的元素"""
    filter_list = []
    for info in Tutor_info:
        has_forbidden = False
        for word in Blocked_words:
            if word and word in info:
                has_forbidden = True
                break
        if not has_forbidden:
            filter_list.append(info)
    return filter_list


def sorted_tutors(Personal_info, filter_res):
    """按个人信息匹配度从高到低排序"""
    match_criteria = list(Personal_info.values())

    def get_match_count(info):
        count = 0
        for value in match_criteria:
            if value in info:
                count += 1
        return count

    return sorted(filter_res, key=get_match_count, reverse=True)


def read_file(file_name):
    """读取文件内容"""
    base = get_data_dir()
    path = os.path.join(base, file_name)
    if not os.path.exists(path):
        return ''
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def save_file(file_name, content):
    """保存（覆盖）文件内容"""
    base = ensure_data_files()
    with open(os.path.join(base, file_name), 'w', encoding='utf-8') as f:
        f.write(content)


def append_file(file_name, content):
    """向文件末尾追加内容"""
    base = ensure_data_files()
    with open(os.path.join(base, file_name), 'a', encoding='utf-8') as f:
        f.write(content)


def run_pipeline():
    """执行完整流程：读取 -> 过滤 -> 排序 -> 保存结果"""
    Blocked_words, Personal_info, Tutor_info = read_txt()
    if Blocked_words is None:
        return {'error': '数据文件读取失败，请检查数据目录'}

    filter_res = filter_tutors(Blocked_words, Tutor_info)
    sort_res = sorted_tutors(Personal_info, filter_res)

    base = ensure_data_files()
    with open(os.path.join(base, 'res.txt'), 'w', encoding='utf-8') as f:
        for index, tutor in enumerate(sort_res, 1):
            f.write("===== 第 {} 个 =====\n".format(index))
            f.write(tutor + '\n\n')

    return {
        'total': len(Tutor_info),
        'filtered_out': len(Tutor_info) - len(filter_res),
        'kept': len(filter_res),
        'result': sort_res,
    }
