"""家教信息筛选排序系统 -- Android 应用入口（Toga / BeeWare）"""
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW

from tutorfilter import tutor_filter


class TutorFilterApp(toga.App):
    def startup(self):
        # 在 Android 上使用应用私有可写目录存放数据文件，
        # 并将打包进 APK 的默认数据复制过去。
        try:
            tutor_filter.set_data_dir(str(self.paths.data))
        except Exception:
            pass
        tutor_filter.ensure_data_files()

        # 主容器
        main_box = toga.Box(style=Pack(direction=COLUMN, padding=10))

        # 标题
        title = toga.Label(
            '家教信息筛选排序系统',
            style=Pack(font_size=18, font_weight='bold', padding_bottom=10)
        )
        main_box.add(title)

        # 文件选择
        file_box = toga.Box(style=Pack(direction=ROW, padding_bottom=5))
        file_box.add(toga.Label('选择文件:', style=Pack(width=80)))
        self.file_select = toga.Selection(
            items=tutor_filter.DATA_FILES,
            style=Pack(flex=1)
        )
        self.file_select.on_select = self.on_file_select
        file_box.add(self.file_select)
        main_box.add(file_box)

        # 文本编辑区
        self.editor = toga.MultilineTextInput(
            style=Pack(flex=1, padding_bottom=5, height=150),
            placeholder='文件内容将显示在这里...'
        )
        main_box.add(self.editor)

        # 文件操作按钮
        btn_box = toga.Box(style=Pack(direction=ROW, padding_bottom=10))
        self.load_btn = toga.Button('加载', on_press=self.on_load, style=Pack(flex=1, padding_right=5))
        self.save_btn = toga.Button('保存', on_press=self.on_save, style=Pack(flex=1, padding_right=5))
        self.clear_btn = toga.Button('清空', on_press=self.on_clear, style=Pack(flex=1, padding_right=5))
        self.append_btn = toga.Button('追加', on_press=self.on_append, style=Pack(flex=1))
        btn_box.add(self.load_btn)
        btn_box.add(self.save_btn)
        btn_box.add(self.clear_btn)
        btn_box.add(self.append_btn)
        main_box.add(btn_box)

        # 运行按钮
        self.run_btn = toga.Button(
            '运行筛选排序',
            on_press=self.on_run,
            style=Pack(padding_bottom=10, height=40)
        )
        main_box.add(self.run_btn)

        # 统计区
        stats_box = toga.Box(style=Pack(direction=ROW, padding_bottom=10))
        self.stat_total = toga.Label('总数: 0', style=Pack(flex=1))
        self.stat_out = toga.Label('过滤: 0', style=Pack(flex=1))
        self.stat_keep = toga.Label('保留: 0', style=Pack(flex=1))
        stats_box.add(self.stat_total)
        stats_box.add(self.stat_out)
        stats_box.add(self.stat_keep)
        main_box.add(stats_box)

        # 结果区
        main_box.add(toga.Label('筛选结果:', style=Pack(padding_bottom=5)))
        self.result_area = toga.MultilineTextInput(
            style=Pack(flex=2, height=200),
            placeholder='运行后将显示筛选结果...'
        )
        main_box.add(self.result_area)

        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = main_box
        self.main_window.show()

        # 加载默认文件
        self.on_load(None)

    def on_file_select(self, widget):
        self.on_load(None)

    def on_load(self, widget):
        fname = self.file_select.value
        content = tutor_filter.read_file(fname)
        self.editor.value = content

    def on_save(self, widget):
        fname = self.file_select.value
        tutor_filter.save_file(fname, self.editor.value)
        self.main_window.info_dialog('提示', '已保存：' + fname)

    def on_clear(self, widget):
        fname = self.file_select.value
        tutor_filter.save_file(fname, '')
        self.editor.value = ''
        self.main_window.info_dialog('提示', '已清空：' + fname)

    def on_append(self, widget):
        fname = self.file_select.value
        text = self.editor.value
        if not text.strip():
            self.main_window.error_dialog('错误', '内容为空，无法追加')
            return
        tutor_filter.append_file(fname, text + '\n')
        self.editor.value = ''
        self.main_window.info_dialog('提示', '已追加到：' + fname)

    def on_run(self, widget):
        self.run_btn.enabled = False
        self.run_btn.text = '运行中...'

        try:
            result = tutor_filter.run_pipeline()
            if 'error' in result:
                self.main_window.error_dialog('错误', result['error'])
                self.result_area.value = '错误: ' + result['error']
                return

            # 更新统计
            self.stat_total.text = '总数: ' + str(result['total'])
            self.stat_out.text = '过滤: ' + str(result['filtered_out'])
            self.stat_keep.text = '保留: ' + str(result['kept'])

            # 构建结果
            lines = ['筛选排序完成！\n']
            lines.append('家教总数：' + str(result['total']) + '   被过滤：' + str(result['filtered_out']) + '   保留：' + str(result['kept']) + '\n')
            for i, tutor in enumerate(result['result'], 1):
                lines.append('===== 第 ' + str(i) + ' 个 =====')
                lines.append(tutor)
                lines.append('')

            self.result_area.value = '\n'.join(lines)
            self.main_window.info_dialog('成功', '筛选排序完成！')

        except Exception as e:
            self.result_area.value = '运行失败：' + str(e)
            self.main_window.error_dialog('错误', '运行失败：' + str(e))
        finally:
            self.run_btn.enabled = True
            self.run_btn.text = '运行筛选排序'


def main():
    return TutorFilterApp()
