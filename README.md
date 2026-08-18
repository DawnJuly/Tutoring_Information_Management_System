# 家教信息筛选排序系统

一个基于 Python 的家教信息筛选与排序工具：根据「屏蔽词」过滤不符合要求的家教，再按「个人信息」匹配度降序排序，最终结果保存到 `res.txt`。提供命令行、Web 界面、Android 应用三种使用方式。

---

## 功能特性

- **屏蔽词过滤**：自动剔除包含任意屏蔽词的家教信息
- **匹配度排序**：按家教信息与个人需求的匹配次数从高到低排序
- **结果持久化**：排序结果自动保存到 `res.txt`
- **文件管理**：支持查看、重置（清空）、追加内容到数据文件
- **多平台支持**：命令行、Web 界面、Android APK

---

## 目录结构

```
.
├── data/                          # 数据文件
│   ├── Blocked_words.txt          # 屏蔽词列表
│   ├── Personal_info.txt          # 个人信息匹配条件
│   ├── Tutor_info.txt             # 家教信息源
│   └── res.txt                    # 排序结果输出
├── web/                           # 网页版
│   ├── server.py                  # 后端服务
│   └── index.html                 # 前端页面
├── android/                       # Android 端
│   ├── src/tutorfilter/
│   │   ├── app.py                 # Toga UI
│   │   ├── tutor_filter.py        # 核心算法
│   │   └── data/                  # 内置默认数据
│   ├── pyproject.toml             # Briefcase 配置
│   └── bin/
│       └── 家教信息筛选排序系统.apk   # 生成的安装包
├── teach.py                       # 命令行版核心逻辑
└── README.md                      # 本文件
```

---

## 快速开始

### 环境要求

- Python 3.6+
- 命令行版：纯标准库，无需安装第三方包
- Web 版：纯标准库，无需安装第三方包
- Android 版：需安装 [Briefcase](https://briefcase.readthedocs.io/)

---

### 方式一：命令行使用

```bash
python teach.py
```

按提示操作：

| 输入 | 含义 |
|------|------|
| `0` | 不需要修改，直接执行筛选排序并退出 |
| `1` | 修改文件（可选择重置 / 新增） |
| `3` | 查看文件内容 |
| `finish` | 结束修改任务并执行筛选排序 |

数据文件位于 `data/` 目录下。

---

### 方式二：Web 界面使用

```bash
python web/server.py
```

浏览器打开 **http://127.0.0.1:8000**

> 注意：不要直接双击 `index.html`，必须通过服务器地址访问。

---

### 方式三：Android 应用

1. 将 `android/bin/家教信息筛选排序系统.apk` 传输到手机
2. 点击安装（需允许「安装未知来源应用」）
3. 打开应用即可使用

APK 构建方式（开发者）：

```bash
cd android
briefcase create android
briefcase build android
```

---

## 数据文件格式

### Blocked_words.txt（屏蔽词）

每行一个或多个屏蔽词，多个词用中文顿号 `、` 分隔：

```
英语、语文、ket
女大学生、女老师
佛山、汕头、惠州
```

### Personal_info.txt（个人信息）

每行一条，格式为 `键：值`（冒号为中文全角冒号 `：`）：

```
地址：黄埔区、天河区、海珠区、番禺区
年级：五年级、六年级、初一、初二、初三、高一、高二
科目：数学、物理
时薪：110/小时、120/小时、130/小时
```

### Tutor_info.txt（家教信息）

每条家教信息之间用**空行**分隔：

```
【编号】8223
【地址】天河区华景新天地
【年级】五年级
【科目】数学

【编号】8224
【地址】番禺区祈福新村
【年级】初三
【科目】物理
```

---

## Web 服务端 API

| 方法 | 路径 | 参数 | 说明 |
|------|------|------|------|
| GET | `/api/view` | `?file=文件名` | 查看文件内容 |
| POST | `/api/reset` | `{"file": "文件名"}` | 清空文件 |
| POST | `/api/append` | `{"file": "文件名", "content": "内容"}` | 追加内容 |
| POST | `/api/run` | — | 执行筛选排序并返回结果 |

可用文件名：`Blocked_words.txt`、`Personal_info.txt`、`Tutor_info.txt`、`res.txt`

---

## 核心算法说明

### 过滤逻辑

遍历所有家教信息，若包含任意屏蔽词则剔除：

```python
def filter_tutors(Blocked_words, Tutor_info):
    filter_list = []
    for info in Tutor_info:
        has_forbidden = False
        for word in Blocked_words:
            if word in info:
                has_forbidden = True
                break
        if not has_forbidden:
            filter_list.append(info)
    return filter_list
```

### 排序逻辑

按个人信息匹配次数降序排列：

```python
def sorted_tutors(Personal_info, filter_res):
    match_criteria = list(Personal_info.values())

    def get_match_count(info):
        count = 0
        for value in match_criteria:
            if value in info:
                count += 1
        return count

    return sorted(filter_res, key=get_match_count, reverse=True)
```

---

## 常见问题

**Q：Web 界面提示「请求失败，请确认服务已启动」？**

1. 确认是通过 `http://127.0.0.1:8000` 访问，而不是双击打开 `index.html`
2. 确认 `python web/server.py` 已成功启动
3. 端口被占用时，修改 `web/server.py` 末尾的 `port = 8000` 为其他端口

**Q：找不到 txt 文件？**

确认数据文件在 `data/` 目录下，且文件名完全一致。

**Q：Android 应用首次启动数据为空？**

应用首次启动会自动将内置默认数据复制到私有存储，请稍等片刻后重新加载。

---

## License

MIT
