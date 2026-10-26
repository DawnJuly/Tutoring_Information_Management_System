"""核心逻辑：纯函数，无 I/O。行为规格见 docs/SPEC.md §2-§3。"""
from typing import NamedTuple


class Scored(NamedTuple):
    entry: str
    score: int
    matched: list  # 命中的键名，如 ["地址", "科目"]


class RunResult(NamedTuple):
    total: int
    filtered_out: int
    kept: int
    results: list  # list[Scored]，按匹配度降序，同分保持原顺序


def parse_blocked_words(text):
    """屏蔽词文本 → 词列表。顿号切分，丢弃空片段（空串会匹配一切）。"""
    words = []
    for line in text.splitlines():
        words.extend(part.strip() for part in line.split("、"))
    return [w for w in words if w]


def parse_personal_info(text):
    """「键：值」文本 → {键: [备选词]}。取第一个全角冒号，值内冒号不切分。"""
    info = {}
    for line in text.splitlines():
        key, sep, value = line.strip().partition("：")
        if not sep or not key:
            continue
        terms = [t.strip() for t in value.split("、")]
        info[key] = [t for t in terms if t]
    return info


def parse_tutor_info(text):
    """家教信息文本 → 条目列表。按空行分段，CRLF 归一，丢弃空段。"""
    return [blk.strip() for blk in text.replace("\r\n", "\n").split("\n\n") if blk.strip()]


def _matched_keys(entry, personal_info):
    matched = []
    for key, terms in personal_info.items():
        if any(t in entry for t in terms):
            matched.append(key)
    return matched


def run(blocked_text, personal_text, tutor_text):
    """完整流水线：解析 → 过滤 → 计分 → 降序稳定排序。"""
    blocked = parse_blocked_words(blocked_text)
    personal = parse_personal_info(personal_text)
    entries = parse_tutor_info(tutor_text)

    kept = [e for e in entries if not any(w in e for w in blocked)]
    scored = [Scored(e, len(m), m) for e, m in
              ((e, _matched_keys(e, personal)) for e in kept)]
    scored.sort(key=lambda s: s.score, reverse=True)  # sorted 稳定，同分保持原顺序

    return RunResult(len(entries), len(entries) - len(kept), len(kept), scored)


def format_result(results):
    """按 res.txt 的既定格式输出（v1 兼容）。"""
    return "".join(
        f"===== 第 {i} 个 =====\n{s.entry}\n\n" for i, s in enumerate(results, 1)
    )
