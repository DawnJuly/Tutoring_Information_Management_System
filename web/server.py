"""家教信息筛选排序系统 — 本地 Web 服务端（纯标准库）。

运行：python web/server.py [端口]   →  http://127.0.0.1:8000
API 契约见 docs/SPEC.md §4。
"""
import json
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from tutorfilter import core, storage  # noqa: E402

WEB_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = storage.default_data_dir()

FILE_LABELS = {
    "Blocked_words.txt": "屏蔽词",
    "Personal_info.txt": "个人信息",
    "Tutor_info.txt": "家教信息",
    "res.txt": "排序结果",
}


def run_pipeline():
    result = storage.run(DATA_DIR)
    personal = core.parse_personal_info(storage.read_file(DATA_DIR, "Personal_info.txt"))
    return {
        "total": result.total,
        "filtered_out": result.filtered_out,
        "kept": result.kept,
        "personal": personal,
        "results": [{"entry": s.entry, "score": s.score, "matched": s.matched}
                    for s in result.results],
    }


class Handler(BaseHTTPRequestHandler):

    def _json(self, code, obj):
        data = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _html(self):
        with open(os.path.join(WEB_DIR, "index.html"), "rb") as f:
            body = f.read()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Cache-Control", "no-store")  # 本地工具，改版即生效
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _body(self):
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length).decode("utf-8") if length else ""
        try:
            return json.loads(raw) if raw else {}
        except json.JSONDecodeError:
            return None

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/":
            self._html()
        elif parsed.path == "/api/view":
            name = parse_qs(parsed.query).get("file", [""])[0]
            if name not in FILE_LABELS:
                self._json(400, {"ok": False, "error": "无效的文件名"})
                return
            try:
                self._json(200, {"ok": True, "file": name,
                                 "content": storage.read_file(DATA_DIR, name)})
            except FileNotFoundError:
                self._json(404, {"ok": False, "error": f"未找到文件：{name}"})
        else:
            self._json(404, {"ok": False, "error": "接口不存在"})

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/run":
            try:
                self._json(200, {"ok": True, **run_pipeline()})
            except (FileNotFoundError, OSError) as e:
                self._json(500, {"ok": False, "error": f"运行失败：{e}"})
            return

        data = self._body()
        if data is None:
            self._json(400, {"ok": False, "error": "请求体不是合法 JSON"})
            return
        name = data.get("file", "")
        if name not in FILE_LABELS:
            self._json(400, {"ok": False, "error": "无效的文件名"})
            return

        try:
            if parsed.path == "/api/reset":
                storage.reset_file(DATA_DIR, name)
                self._json(200, {"ok": True, "msg": f"已重置：{name}"})
            elif parsed.path == "/api/append":
                storage.append_file(DATA_DIR, name, data.get("content", ""))
                self._json(200, {"ok": True, "msg": f"已新增内容到：{name}"})
            else:
                self._json(404, {"ok": False, "error": "接口不存在"})
        except OSError as e:
            self._json(500, {"ok": False, "error": f"写入失败：{e}"})

    def log_message(self, format, *args):
        print(f"[{self.command} {self.path}]", file=sys.stderr, flush=True)  # 临时调试日志


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"[OK] 服务已启动：http://127.0.0.1:{port}（Ctrl+C 停止）")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n服务已停止")
        server.server_close()


if __name__ == "__main__":
    main()
