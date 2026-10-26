"""命令行入口：跑一遍流水线，打印摘要与前列结果，写 res.txt。"""
import argparse
import sys

from tutorfilter import storage


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="tutorfilter", description="家教信息筛选排序：屏蔽词过滤 + 匹配度排序"
    )
    parser.add_argument("-d", "--data-dir", default=storage.default_data_dir(),
                        help="数据目录（默认：项目内 data/）")
    parser.add_argument("-n", "--top", type=int, default=5, metavar="N",
                        help="终端预览前 N 条结果（默认 5，完整结果始终写入 res.txt）")
    args = parser.parse_args(argv)

    try:
        result = storage.run(args.data_dir)
    except FileNotFoundError as e:
        print(f"错误：{e}", file=sys.stderr)
        return 1

    print(f"家教信息 {result.total} 条，屏蔽过滤 {result.filtered_out} 条，保留 {result.kept} 条")
    for i, s in enumerate(result.results[:max(args.top, 0)], 1):
        keys = "、".join(s.matched) if s.matched else "无匹配项"
        print(f"\n第 {i} 名（匹配 {s.score} 项：{keys}）\n{s.entry}")
    print(f"\n[OK] 完整排序结果已写入：{args.data_dir}\\res.txt")
    return 0


if __name__ == "__main__":
    sys.exit(main())
