# -*- coding: utf-8 -*-
"""
家教信息筛选排序系统 —— 本地 Web 服务端（纯标准库，无需安装任何第三方包）

运行方式：
    python server.py

然后在浏览器打开：http://127.0.0.1:8000

要求：本文件、index.html、teach.py 以及各 txt 文件放在同一目录下。
"""
import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

# 复用 teach.py 中的核心逻辑（只导入函数，不会执行其 __main__ 部分）
from teach import read_txt, filter_tutors, sorted_tutors

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 允许操作的文件（文件名 -> 中文说明）
FILES = {
    'Blocked_words.txt': '屏蔽词',
    'Personal_info.txt': '个人信息',
    'Tutor_info.txt': '家教信息',
    'res.txt': '排序结果',
}


def _path(name):
    return os.path.join(BASE_DIR, name)


def view_file(name):
    """读取文件内容，文件不存在返回 None"""
    p = _path(name)
    if not os.path.exists(p):
        return None
    with open(p, 'r', encoding='utf-8') as f:
        return f.read()


def reset_file(name):
    """清空文件内容"""
    with open(_path(name), 'w', encoding='utf-8') as f:
        f.write('')


def append_file(name, content):
    """向文件末尾追加内容"""
    with open(_path(name), 'a', encoding='utf-8') as f:
        f.write(content)


def run_pipeline():
    """执行完整流程：读取 -> 过滤 -> 排序 -> 保存结果"""
    Blocked_words, Personal_info, Tutor_info = read_txt()
    filter_res = filter_tutors(Blocked_words, Tutor_info)
    sort_res = sorted_tutors(Personal_info, filter_res)

    reset_file('res.txt')
    with open(_path('res.txt'), 'a', encoding='utf-8') as f:
        for index, tutor in enumerate(sort_res, 1):
            f.write(f"===== 第 {index} 个 =====\n")
            f.write(tutor + '\n\n')

    return {
        'total': len(Tutor_info),
        'filtered_out': len(Tutor_info) - len(filter_res),
        'kept': len(filter_res),
        'result': sort_res,
    }


class Handler(BaseHTTPRequestHandler):

    def _send_json(self, code, obj):
        data = json.dumps(obj, ensure_ascii=False).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _send_html(self):
        html_path = os.path.join(BASE_DIR, 'index.html')
        if not os.path.exists(html_path):
            self._send_json(404, {'ok': False, 'error': '未找到 index.html，请确认它与 server.py 在同一目录'})
            return
        with open(html_path, 'r', encoding='utf-8') as f:
            html = f.read().encode('utf-8')
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', str(len(html)))
        self.end_headers()
        self.wfile.write(html)

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == '/':
            self._send_html()
        elif parsed.path == '/api/view':
            qs = parse_qs(parsed.query)
            name = qs.get('file', [''])[0]
            if name not in FILES:
                self._send_json(400, {'ok': False, 'error': '无效的文件名'})
                return
            content = view_file(name)
            if content is None:
                self._send_json(404, {'ok': False, 'error': f'未找到文件：{name}'})
            else:
                self._send_json(200, {'ok': True, 'file': name, 'content': content})
        else:
            self._send_json(404, {'ok': False, 'error': '接口不存在'})

    def do_POST(self):
        parsed = urlparse(self.path)
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length).decode('utf-8')
        try:
            data = json.loads(body) if body else {}
        except json.JSONDecodeError:
            self._send_json(400, {'ok': False, 'error': '请求体不是合法 JSON'})
            return

        if parsed.path == '/api/reset':
            name = data.get('file', '')
            if name not in FILES:
                self._send_json(400, {'ok': False, 'error': '无效的文件名'})
                return
            reset_file(name)
            self._send_json(200, {'ok': True, 'msg': f'已重置：{name}'})
        elif parsed.path == '/api/append':
            name = data.get('file', '')
            content = data.get('content', '')
            if name not in FILES:
                self._send_json(400, {'ok': False, 'error': '无效的文件名'})
                return
            append_file(name, content)
            self._send_json(200, {'ok': True, 'msg': f'已新增内容到：{name}'})
        elif parsed.path == '/api/run':
            try:
                result = run_pipeline()
                self._send_json(200, {'ok': True, **result})
            except Exception as e:
                self._send_json(500, {'ok': False, 'error': f'运行失败：{e}'})
        else:
            self._send_json(404, {'ok': False, 'error': '接口不存在'})

    def log_message(self, format, *args):
        pass  # 关闭默认请求日志，保持控制台整洁


def main():
    port = 8000
    server = HTTPServer(('127.0.0.1', port), Handler)
    print('✅ 服务已启动，请用浏览器打开：http://127.0.0.1:%d' % port)
    print('   按 Ctrl+C 停止服务')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\n服务已停止')
        server.server_close()


if __name__ == '__main__':
    main()