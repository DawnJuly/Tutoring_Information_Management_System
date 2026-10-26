"""家教信息筛选排序系统 -- Android 核心算法模块（vendored 副本）

算法与项目根目录 tutorfilter/core.py（v2 语义）保持一致，须同步修改：
- 匹配度按「键」计分：键的任意备选词命中即该键得 1 分（v1 用整条值串匹配，实际永远 0 分）
- 屏蔽词/备选词解析丢弃空片段（空串是任何文本的子串，会误杀全部数据）
- 排序稳定：同分保持原文件顺序

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


def parse_blocked_words(text):
    """屏蔽词文本 → 词列表。顿号切分，丢弃空片段。"""
    words = []
    for line in text.splitlines():
        words.extend(part.strip() for part in line.split('、'))
    return [w for w in words if w]


def parse_personal_info(text):
    """「键：值」文本 → {键: [备选词]}。取第一个全角冒号，值内冒号不切分。"""
    info = {}
    for line in text.splitlines():
        key, sep, value = line.strip().partition('：')
        if not sep or not key:
            continue
        terms = [t.strip() for t in value.split('、')]
        info[key] = [t for t in terms if t]
    return info


def parse_tutor_info(text):
    """家教信息文本 → 条目列表。按空行分段，CRLF 归一，丢弃空段。"""
    return [blk.strip() for blk in text.replace('\r\n', '\n').split('\n\n') if blk.strip()]


def read_txt():
    """读取三个数据文件，返回 (Blocked_words, Personal_info, Tutor_info)；缺文件返回 (None, None, None)"""
    base = ensure_data_files()
    try:
        with open(os.path.join(base, 'Blocked_words.txt'), 'r', encoding='utf-8') as f:
            blocked = parse_blocked_words(f.read())
        with open(os.path.join(base, 'Personal_info.txt'), 'r', encoding='utf-8') as f:
            personal = parse_personal_info(f.read())
        with open(os.path.join(base, 'Tutor_info.txt'), 'r', encoding='utf-8') as f:
            entries = parse_tutor_info(f.read())
    except FileNotFoundError:
        return None, None, None
    return blocked, personal, entries


def filter_tutors(Blocked_words, Tutor_info):
    """遍历筛选：移除包含任意屏蔽词的元素"""
    return [e for e in Tutor_info if not any(w and w in e for w in Blocked_words)]


def matched_keys(entry, Personal_info):
    """按键匹配：键的任意备选词是条目子串，则该键命中"""
    matched = []
    for key, terms in Personal_info.items():
        if any(t in entry for t in terms):
            matched.append(key)
    return matched


def sorted_tutors(Personal_info, filter_res):
    """按匹配度（命中键数）降序稳定排序，返回 [(条目, 分数, 命中键)]"""
    scored = [(e, len(m), m) for e, m in
              ((e, matched_keys(e, Personal_info)) for e in filter_res)]
    scored.sort(key=lambda s: s[1], reverse=True)
    return scored


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
    """执行完整流程：读取 -> 过滤 -> 计分排序 -> 保存结果"""
    Blocked_words, Personal_info, Tutor_info = read_txt()
    if Blocked_words is None:
        return {'error': '数据文件读取失败，请检查数据目录'}

    filter_res = filter_tutors(Blocked_words, Tutor_info)
    scored = sorted_tutors(Personal_info, filter_res)

    base = ensure_data_files()
    with open(os.path.join(base, 'res.txt'), 'w', encoding='utf-8') as f:
        for index, (tutor, score, matched) in enumerate(scored, 1):
            f.write("===== 第 {} 个（匹配 {} 项：{}）=====\n".format(
                index, score, '、'.join(matched) if matched else '无'))
            f.write(tutor + '\n\n')

    return {
        'total': len(Tutor_info),
        'filtered_out': len(Tutor_info) - len(filter_res),
        'kept': len(filter_res),
        'result': [t for t, score, matched in scored],
    }
