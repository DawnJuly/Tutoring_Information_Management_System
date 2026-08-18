def read_txt():
    import os
    base = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
    # 读取屏蔽词文件
    try:
        with open(os.path.join(base, 'Blocked_words.txt'), 'r', encoding='utf-8') as f:
            Blocked_words = []
            for line in f.readlines():
                line = line.strip()
                Blocked_words.extend(line.split('、'))
    except FileNotFoundError:
        print("错误：未找到 Blocked_words.txt 文件，请确认文件在 data 目录下")
        return

    # 读取个人信息文件
    try:
        with open(os.path.join(base, 'Personal_info.txt'), 'r', encoding='utf-8') as f:
            Personal_info = {}
            for line in f.readlines():
                line = line.strip().split('：')
                Personal_info[line[0]] = line[-1]
    except FileNotFoundError:
        print("错误：未找到 Personal_info.txt 文件，请确认文件在 data 目录下")
        return

    # 读取家教信息文件
    try:
        with open(os.path.join(base, 'Tutor_info.txt'), 'r', encoding='utf-8') as f:
            content = f.read()
            # 按两个换行符（完整空行）切分段落
            content = content.replace('\r\n', '\n')
            Tutor_info = content.split('\n\n')
    except FileNotFoundError:
        print("错误：未找到 Tutor_info.txt 文件，请确认文件在 data 目录下")
        return
    return Blocked_words, Personal_info, Tutor_info

def filter_tutors(Blocked_words, Tutor_info):
    # 遍历筛选：移除包含任意屏蔽词的元素
    filter_list = []
    for info in Tutor_info:
        # 检查是否包含屏蔽词
        has_forbidden = False
        for word in Blocked_words:
            if word in info:
                has_forbidden = True
                break
        if not has_forbidden:
            filter_list.append(info)
    return filter_list

def sorted_tutors(Personal_info, filter_res):
    # 提取个人信息的所有值，作为匹配判定标准
    match_criteria = list(Personal_info.values())

    # 计算单条家教信息的匹配次数
    def get_match_count(info):
        count = 0
        for value in match_criteria:
            if value in info:
                count += 1
        return count

    # 按匹配次数从高到低排序
    sorted_list = sorted(filter_res, key=get_match_count, reverse=True)
    return sorted_list

def change_txt(file_name, mode='1'):
    """
    修改文件函数：用于更新 Blocked_words.txt / Personal_info.txt / Tutor_info.txt / res.txt
    file_name: 要修改的文件名
    mode: '1' 重置信息（清空文件）；'2' 新增信息（逐行输入，输入 right 结束）
    """
    import os
    base = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')

    if mode == '1':
        # 重置信息：清空文件内容
        with open(os.path.join(base, file_name), 'w', encoding='utf-8') as f:
            f.write('')
        print(f"[OK] 已重置：{file_name}")

    elif mode == '2':
        # 新增信息：逐行输入内容，输入 right 结束
        print(f"请逐行输入要新增到 {file_name} 的内容（输入 right 结束）：")
        new_lines = []
        while True:
            line = input()
            if line.strip() == 'right':
                break
            new_lines.append(line)
        with open(os.path.join(base, file_name), 'a', encoding='utf-8') as f:
            for line in new_lines:
                f.write(line + '\n')
        print(f"[OK] 已新增 {len(new_lines)} 行内容到：{file_name}")

    else:
        print("错误：无效的修改方式")

if __name__ == '__main__':

    files = {
        '0': 'Blocked_words.txt',
        '1': 'Personal_info.txt',
        '2': 'Tutor_info.txt',
        '3': 'res.txt',
    }

    while True:
        # 第一问：是否需要修改txt文件
        need = input("是否需要修改txt文件？（0不需要，1需要，3查看信息，finish结束修改任务）：")
        if need == '0':
            print("不需要修改")
            break
        elif need == 'finish':
            print("结束修改任务")
            break
        elif need == '1':
            # 第二问：选择要修改的文件
            file_choice = input("请选择要修改的文件（0 Blocked_words、1 Personal_info、2 Tutor_info）：")
            if file_choice not in files:
                print("错误：无效的文件选择，请重新选择")
                continue
            # 第三问：选择修改方式
            mode = input("请选择修改方式（1重置信息，2新增信息）：")
            if mode not in ('1', '2'):
                print("错误：无效的修改方式，请重新选择")
                continue
            change_txt(files[file_choice], mode)
        elif need == '3':
            # 第二问：选择要修改的文件
            file_choice = input("请选择要查看的文件（0 Blocked_words、1 Personal_info、2 Tutor_info）：")
            if file_choice not in files:
                print("错误：无效的文件选择，请重新选择")
                continue
            import os
            base = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
            try:
                with open(os.path.join(base, files[file_choice]), 'r', encoding='utf-8') as f:
                    print(f"===== {files[file_choice]} 内容如下 =====")
                    print(f.read())
            except FileNotFoundError:
                print(f"错误：未找到 {files[file_choice]} 文件")
        else:
            print("输入无效，请输入 0、1、3 或 finish")

    Blocked_words, Personal_info, Tutor_info = read_txt()
    filter_res = filter_tutors(Blocked_words, Tutor_info)
    sort_res = sorted_tutors(Personal_info, filter_res)

    # 保存排序结果到 res.txt
    change_txt('res.txt', '1')  # 先重置 res.txt
    import os
    base = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
    with open(os.path.join(base, 'res.txt'), 'a', encoding='utf-8') as f:
        for index, tutor in enumerate(sort_res, 1):
            f.write(f"===== 第 {index} 个 =====\n")
            f.write(tutor + '\n\n')
    print("[OK] 筛选排序结果已保存到：data/res.txt")
