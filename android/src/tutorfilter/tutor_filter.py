"""
家教信息筛选排序系统 —— 核心算法模块
"""
import os


def get_data_dir():
    """获取数据文件目录"""
    # Android 环境
    if 'ANDROID_ARGUMENT' in os.environ:
        from android.storage import app_storage_path
        return app_storage_path()
    # 桌面环境
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')


def ensure_data_files():
    """确保数据文件存在"""
    data_dir = get_data_dir()
    os.makedirs(data_dir, exist_ok=True)

    builtin_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')

    files = ['Blocked_words.txt', 'Personal_info.txt', 'Tutor_info.txt', 'res.txt']
    for fname in files:
        target = os.path.join(data_dir, fname)
        if not os.path.exists(target):
            source = os.path.join(builtin_dir, fname)
            if os.path.exists(source):
                with open(source, 'r', encoding='utf-8') as f:
                    content = f.read()
                with open(target, 'w', encoding='utf-8') as f:
                    f.write(content)
    return data_dir


def read_txt():
    """读取三个数据文件"""
    base = ensure_data_files()

    try:
        with open(os.path.join(base, 'Blocked_words.txt'), 'r', encoding='utf-8') as f:
            Blocked_words = []
            for line in f.readlines():
                line = line.strip()
                if line:
                    Blocked_words.extend(line.split('、'))
    except FileNotFoundError:
        return None, None, None

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

    try:
        with open(os.path.join(base, 'Tutor_info.txt'), 'r', encoding='utf-8') as f:
            content = f.read()
            content = content.replace('\r\n', '\n')
            Tutor_info = [item.strip() for item in content.split('\n\n') if item.strip()]
    except FileNotFoundError:
        return None, None, None

    return Blocked_words, Personal_info, Tutor_info


def filter_tutors(Blocked_words, Tutor_info):
    """屏蔽词过滤"""
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
    """按匹配度排序"""
    match_criteria = list(Personal_info.values())

    def get_match_count(info):
        count = 0
        for value in match_criteria:
            if value in info:
                count += 1
        return count

    return sorted(filter_res, key=get_match_count, reverse=True)


def read_file(file_name):
    """读取文件"""
    base = get_data_dir()
    path = os.path.join(base, file_name)
    if not os.path.exists(path):
        return ''
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def save_file(file_name, content):
    """保存文件"""
    base = get_data_dir()
    with open(os.path.join(base, file_name), 'w', encoding='utf-8') as f:
        f.write(content)


def append_file(file_name, content):
    """追加文件"""
    base = get_data_dir()
    with open(os.path.join(base, file_name), 'a', encoding='utf-8') as f:
        f.write(content)


def run_pipeline():
    """执行完整流程"""
    Blocked_words, Personal_info, Tutor_info = read_txt()
    if Blocked_words is None:
        return {'error': '数据文件读取失败'}

    filter_res = filter_tutors(Blocked_words, Tutor_info)
    sort_res = sorted_tutors(Personal_info, filter_res)

    base = get_data_dir()
    with open(os.path.join(base, 'res.txt'), 'w', encoding='utf-8') as f:
        for index, tutor in enumerate(sort_res, 1):
            f.write(f"===== 第 {index} 个 =====\n")
            f.write(tutor + '\n\n')

    return {
        'total': len(Tutor_info),
        'filtered_out': len(Tutor_info) - len(filter_res),
        'kept': len(filter_res),
        'result': sort_res,
    }
