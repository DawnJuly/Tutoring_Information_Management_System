"""核心逻辑测试：解析、过滤、匹配、排序、流水线。运行：python -m unittest discover tests"""
import unittest

from tutorfilter.core import (
    Scored,
    format_result,
    parse_blocked_words,
    parse_personal_info,
    parse_tutor_info,
    run,
)

BLOCKED_TEXT = "英语、语文\n女大学生、92老师\n\n研究生、\n"
PERSONAL_TEXT = (
    "地址：霞山、城市假日\n"
    "年级：五年级、六年级、初一\n"
    "科目：数学\n"
    "时薪：65/小时\n"
    "这行没有冒号\n"
    "：空键\n"
)
TUTOR_TEXT = (
    "【地址】霞山区城市假日B区\n【年级】五年级\n【科目】数学\n【时薪】65/小时\n\n"
    "【地址】赤坎区\n【年级】高一\n【科目】英语\n\n"
    "【地址】麻章区\n【年级】初三\n【科目】物理\n\n"
    "\r\n【地址】霞山区\r\n【科目】语文\r\n\r\n"
)


class ParseBlockedWordsTest(unittest.TestCase):
    def test_splits_on_ideographic_comma(self):
        self.assertEqual(parse_blocked_words("英语、语文\n"), ["英语", "语文"])

    def test_drops_empty_fragments_and_lines(self):
        # 行尾多余的「、」与空行不得产生空屏蔽词（空串是任何文本的子串，会误杀全部数据）
        self.assertEqual(
            parse_blocked_words(BLOCKED_TEXT),
            ["英语", "语文", "女大学生", "92老师", "研究生"],
        )

    def test_empty_text(self):
        self.assertEqual(parse_blocked_words(""), [])


class ParsePersonalInfoTest(unittest.TestCase):
    def test_key_to_alternatives(self):
        info = parse_personal_info(PERSONAL_TEXT)
        self.assertEqual(
            info,
            {
                "地址": ["霞山", "城市假日"],
                "年级": ["五年级", "六年级", "初一"],
                "科目": ["数学"],
                "时薪": ["65/小时"],
            },
        )

    def test_value_keeps_text_after_further_colons(self):
        info = parse_personal_info("备注：时间：周六上午、周日下午\n")
        self.assertEqual(info, {"备注": ["时间：周六上午", "周日下午"]})

    def test_skips_lines_without_colon_or_key(self):
        self.assertEqual(parse_personal_info("没冒号的行\n：空键\n\n"), {})


class ParseTutorInfoTest(unittest.TestCase):
    def test_splits_on_blank_lines(self):
        entries = parse_tutor_info(TUTOR_TEXT)
        self.assertEqual(len(entries), 4)
        self.assertEqual(entries[0].splitlines()[0], "【地址】霞山区城市假日B区")

    def test_normalizes_crlf(self):
        entries = parse_tutor_info(TUTOR_TEXT)
        self.assertNotIn("\r", entries[3])
        self.assertEqual(entries[3].splitlines()[0], "【地址】霞山区")

    def test_strips_and_drops_empty(self):
        self.assertEqual(parse_tutor_info("  \n\n\n  条目  \n\n"), ["条目"])
        self.assertEqual(parse_tutor_info(""), [])


class RunPipelineTest(unittest.TestCase):
    """端到端：过滤（英语/语文/女大学生/92老师/研究生）→ 匹配计分 → 稳定降序。"""

    def setUp(self):
        self.result = run(BLOCKED_TEXT, PERSONAL_TEXT, TUTOR_TEXT)

    def test_counts(self):
        # 4 条：条目2 含「英语」被屏蔽；条目4 含「语文」被屏蔽
        self.assertEqual((self.result.total, self.result.filtered_out, self.result.kept), (4, 2, 2))

    def test_v2_matching_is_per_key_any_term(self):
        # v1 用整条值串匹配导致全 0 分；v2 按备选词匹配
        # 条目1：地址✓(霞山) 年级✓(五年级) 科目✓(数学) 时薪✓(65/小时) = 4
        # 条目3：地址✗ 年级✗(初三不在备选) 科目✗ 时薪✗ = 0
        self.assertEqual(
            [(s.entry.splitlines()[0], s.score, s.matched) for s in self.result.results],
            [
                ("【地址】霞山区城市假日B区", 4, ["地址", "年级", "科目", "时薪"]),
                ("【地址】麻章区", 0, []),
            ],
        )

    def test_same_key_multiple_terms_count_once(self):
        result = run("", "地址：霞山、城市假日\n", "【地址】霞山区城市假日\n")
        self.assertEqual(result.results[0].score, 1)

    def test_sort_is_descending_and_stable(self):
        text = "【科目】物理\n\n【科目】数学\n\n【地址】霞山\n【科目】数学\n\n"
        result = run("", "地址：霞山\n科目：数学\n", text)
        self.assertEqual([s.score for s in result.results], [2, 1, 0])
        # 同分的条目保持原文件顺序
        self.assertEqual(result.results[1].entry, "【科目】数学")
        self.assertEqual(result.results[2].entry, "【科目】物理")

    def test_empty_blocked_words_keeps_all(self):
        result = run("", PERSONAL_TEXT, TUTOR_TEXT)
        self.assertEqual(result.kept, 4)

    def test_empty_texts_are_valid(self):
        result = run("", "", "")
        self.assertEqual((result.total, result.kept), (0, 0))
        self.assertEqual(result.results, [])


class FormatResultTest(unittest.TestCase):
    def test_format(self):
        scored = [Scored("条目A", 2, []), Scored("条目B", 0, [])]
        self.assertEqual(
            format_result(scored),
            "===== 第 1 个 =====\n条目A\n\n===== 第 2 个 =====\n条目B\n\n",
        )


if __name__ == "__main__":
    unittest.main()
