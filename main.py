import os
import sys
import json
import random
from datetime import datetime
from math import cos, sin, pi
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.widget import Widget
from kivy.uix.floatlayout import FloatLayout
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.core.text import LabelBase
from kivy.graphics import Color, Rectangle, Ellipse, Line, Mesh, PushMatrix, PopMatrix, Rotate

def resource_path(relative_path):
    """取得資源檔案的絕對路徑，支援 Android 打包後的路徑"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)

# ---------- 中文字體設定 ----------
font_path = resource_path('msyh.ttf')
LabelBase.register(name='Roboto', fn_regular=font_path)

# ---------- 自訂扁平化按鈕（無外框、透明背景、文字加粗、黑色描邊） ----------
class FlatButton(Button):
    def __init__(self, **kwargs):
        kwargs.setdefault('font_size', 20)
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_down = ''
        self.background_color = (0, 0, 0, 0)
        self.border = (0, 0, 0, 0)
        self.bold = True
        self.outline_width = 2
        self.outline_color = (0, 0, 0, 1)
        self.color = (1, 1, 1, 1)

# ---------- 語言字典 ----------
TRANSLATIONS = {
    'zh': {
        'ready_focus': '準備好開始專注了嗎？',
        'focusing': '專注中...',
        'paused': '已暫停',
        'start': '開始專注',
        'pause': '暫停',
        'resume': '繼續',
        'reset': '重置',
        'history': '歷史記錄',
        'white_noise_on': '白噪音：開',
        'white_noise_off': '白噪音：關',
        'playing': '播放中',
        'stopped': '已關閉',
        'return_timer': '返回計時器',
        'history_title': '專注歷史',
        'total_focus': '總專注時間：',
        'no_history': '尚無專注記錄',
        'session_format': '{date}  {duration}',
        'notification_pause_title': 'FocusPods 提醒',
        'notification_pause_msg': '你正在學習！已自動暫停計時，快回來繼續吧！',
        'popup_welcome_title': '歡迎回來',
        'popup_welcome_msg': '你剛才暫停了計時，繼續加油哦！',
        'lang_zh': '中文',
        'lang_en': 'English',
        'switch_noise': '切換音效'
    },
    'en': {
        'ready_focus': 'Ready to focus?',
        'focusing': 'Focusing...',
        'paused': 'Paused',
        'start': 'Start Focus',
        'pause': 'Pause',
        'resume': 'Resume',
        'reset': 'Reset',
        'history': 'History',
        'white_noise_on': 'White Noise: On',
        'white_noise_off': 'White Noise: Off',
        'playing': 'Playing',
        'stopped': 'Off',
        'return_timer': 'Back to Timer',
        'history_title': 'Focus History',
        'total_focus': 'Total focus time: ',
        'no_history': 'No focus sessions yet',
        'session_format': '{date}  {duration}',
        'notification_pause_title': 'FocusPods Reminder',
        'notification_pause_msg': 'You are studying! Timer paused, come back and continue!',
        'popup_welcome_title': 'Welcome Back',
        'popup_welcome_msg': 'You paused the timer, keep going!',
        'lang_zh': '中文',
        'lang_en': 'English',
        'switch_noise': 'Switch Sound'
    }
}

current_lang = 'zh'

def get_text(key):
    return TRANSLATIONS[current_lang].get(key, key)

# ---------- 輔助函數 ----------
def load_user_data():
    data_path = os.path.join(App.get_running_app().user_data_dir, 'user_data.json')
    default_data = {'language': 'zh', 'history': []}
    if os.path.exists(data_path):
        with open(data_path, 'r') as f:
            data = json.load(f)
            for key, value in default_data.items():
                if key not in data:
                    data[key] = value
            return data
    return default_data

def save_user_data(data):
    data_path = os.path.join(App.get_running_app().user_data_dir, 'user_data.json')
    with open(data_path, 'w') as f:
        json.dump(data, f, indent=4)

def format_duration(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    if hours > 0:
        return f'{hours:02d}:{minutes:02d}:{secs:02d}'
    else:
        return f'{minutes:02d}:{secs:02d}'

# ---------- 背景 Widget ----------
class BackgroundWidget(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.bind(size=self._update_canvas, pos=self._update_canvas)
        self._update_canvas()

    def _update_canvas(self, *args):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(0.79, 0.98, 0.84, 1)
            Rectangle(pos=self.pos, size=self.size)

            w, h = self.width, self.height

            cx, cy = w * 0.7, h * 0.65
            r = min(w, h) * 0.22

            Color(1, 1, 1, 0.3)
            Ellipse(pos=(cx - r, cy - r * 0.9), size=(2 * r, 2 * r * 0.9), width=1.5)
            Ellipse(pos=(cx - r * 0.5, cy - r), size=(r * 1.0, 2 * r), width=1.5)

            PushMatrix()
            Rotate(angle=45, origin=(cx, cy))
            Ellipse(pos=(cx - r * 0.5, cy - r), size=(r * 1.0, 2 * r), width=1.5)
            PopMatrix()

            Ellipse(pos=(cx - r, cy - r * 0.4), size=(2 * r, r * 0.8), width=1.5)
            Ellipse(pos=(cx - r, cy + r * 0.4), size=(2 * r, r * 0.8), width=1.5)

            self._draw_cube(cx - r * 1.8, cy - r * 0.8, r * 0.9)
            self._draw_cube(cx + r * 1.2, cy - r * 0.5, r * 0.7)
            self._draw_cube(cx + r * 0.8, cy + r * 1.0, r * 0.6)

            self._draw_diamond(w * 0.05, h * 0.85, w * 0.04, (1.0, 0.7, 0.7, 0.5))
            self._draw_diamond(w * 0.12, h * 0.85, w * 0.04, (0.7, 0.8, 1.0, 0.5))
            self._draw_diamond(w * 0.05, h * 0.78, w * 0.04, (1.0, 0.95, 0.8, 0.5))
            self._draw_diamond(w * 0.12, h * 0.78, w * 0.04, (0.8, 1.0, 0.8, 0.5))

    def _draw_cube(self, cx, cy, size):
        angle = pi / 6
        cos_a = cos(angle)
        sin_a = sin(angle)
        half = size / 2
        vertices = [
            (-half, -half, -half), ( half, -half, -half), ( half,  half, -half), (-half,  half, -half),
            (-half, -half,  half), ( half, -half,  half), ( half,  half,  half), (-half,  half,  half)
        ]
        projected = []
        for x, y, z in vertices:
            sx = cx + (x - y) * cos_a
            sy = cy + (x + y) * sin_a - z
            projected.append((sx, sy))
        edges = [
            (0, 1), (1, 2), (2, 3), (3, 0),
            (4, 5), (5, 6), (6, 7), (7, 4),
            (0, 4), (1, 5), (2, 6), (3, 7)
        ]
        Color(1, 1, 1, 0.6)
        for start, end in edges:
            Line(points=[projected[start][0], projected[start][1],
                         projected[end][0], projected[end][1]], width=1.5)

    def _draw_diamond(self, x, y, size, color):
        half = size / 2
        top = (x, y + half)
        right = (x + half, y)
        bottom = (x, y - half)
        left = (x - half, y)
        vertices = [
            top[0], top[1], 0, 0,
            right[0], right[1], 0, 0,
            bottom[0], bottom[1], 0, 0,
            left[0], left[1], 0, 0
        ]
        indices = [0, 1, 3, 1, 2, 3]
        Color(*color)
        Mesh(vertices=vertices, indices=indices, mode='triangles')

# ---------- 計時器畫面 ----------
class TimerScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.time_seconds = 0
        self.session_seconds = 0
        self.running = False
        self.sound = None

        # 指定音訊檔案（請將實際 WAV 檔案放在與 main.py 相同目錄）
        self.noise_files = [
            resource_path('white_noise1.wav'),
            resource_path('white_noise2.wav'),
        ]
        self.current_noise_index = 0

        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)

        self.timer_label = Label(
            text='00:00:00',
            font_size=60,
            bold=True,
            size_hint=(1, 0.25),
            color=(1,1,1,1),
            outline_width=2,
            outline_color=(0,0,0,1)
        )
        layout.add_widget(self.timer_label)

        self.status_label = Label(
            text='',
            font_size=30,
            bold=True,
            size_hint=(1, 0.12),
            color=(1,1,1,1),
            outline_width=1,
            outline_color=(0,0,0,1)
        )
        layout.add_widget(self.status_label)

        # 白噪音開關
        noise_box = BoxLayout(size_hint=(1, 0.15), spacing=10)
        self.noise_toggle = FlatButton(text='', font_size=30, size_hint=(0.4, 1))
        self.noise_toggle.bind(on_press=self.toggle_noise)
        noise_box.add_widget(self.noise_toggle)
        layout.add_widget(noise_box)

        # 切換音效按鈕
        self.switch_noise_btn = FlatButton(text='', font_size=24, size_hint=(1, 0.1))
        self.switch_noise_btn.bind(on_press=self.switch_noise)
        layout.add_widget(self.switch_noise_btn)

        # 開始/暫停、重置按鈕
        btn_box = BoxLayout(size_hint=(1, 0.2), spacing=15)
        self.start_btn = FlatButton(text='', font_size=30)
        self.start_btn.bind(on_press=self.toggle_timer)
        btn_box.add_widget(self.start_btn)
        self.reset_btn = FlatButton(text='', font_size=30)
        self.reset_btn.bind(on_press=self.reset_timer)
        btn_box.add_widget(self.reset_btn)
        layout.add_widget(btn_box)

        # 歷史記錄按鈕
        nav_box = BoxLayout(size_hint=(1, 0.15), spacing=10)
        self.history_btn = FlatButton(text='', font_size=30)
        self.history_btn.bind(on_press=self.go_to_history)
        nav_box.add_widget(self.history_btn)
        layout.add_widget(nav_box)

        # 語言切換按鈕
        lang_box = BoxLayout(size_hint=(1, 0.15), spacing=10)
        self.zh_btn = FlatButton(text='中文', font_size=30)
        self.zh_btn.bind(on_press=lambda x: App.get_running_app().set_language('zh'))
        lang_box.add_widget(self.zh_btn)
        self.en_btn = FlatButton(text='English', font_size=30)
        self.en_btn.bind(on_press=lambda x: App.get_running_app().set_language('en'))
        lang_box.add_widget(self.en_btn)
        layout.add_widget(lang_box)

        self.add_widget(layout)

        Clock.schedule_interval(self.update_timer, 1.0)
        self.apply_language()

    def get_current_noise_file(self):
        if self.noise_files:
            return self.noise_files[self.current_noise_index]
        return None

    def load_and_play_current_noise(self):
        file_path = self.get_current_noise_file()
        if not file_path:
            return False
        self.sound = SoundLoader.load(file_path)
        if self.sound:
            self.sound.loop = True
            self.sound.play()
            return True
        return False

    def toggle_noise(self, instance):
        if not self.noise_files:
            popup = Popup(title='提示', content=Label(text='找不到音訊檔案'), size_hint=(0.6, 0.4))
            popup.open()
            return
        if self.sound and self.sound.state == 'play':
            self.sound.stop()
            self.noise_toggle.text = get_text('white_noise_on')
        else:
            if self.load_and_play_current_noise():
                self.noise_toggle.text = get_text('white_noise_off')
            else:
                popup = Popup(title='錯誤', content=Label(text='無法載入音訊檔案'), size_hint=(0.6, 0.4))
                popup.open()

    def switch_noise(self, instance):
        if not self.noise_files:
            popup = Popup(title='提示', content=Label(text='找不到音訊檔案'), size_hint=(0.6, 0.4))
            popup.open()
            return
        was_playing = (self.sound and self.sound.state == 'play')
        if was_playing:
            self.sound.stop()
        self.current_noise_index = (self.current_noise_index + 1) % len(self.noise_files)
        if was_playing:
            if not self.load_and_play_current_noise():
                self.noise_toggle.text = get_text('white_noise_on')

    def toggle_timer(self, instance):
        if not self.running:
            self.running = True
            self.session_seconds = 0
        else:
            self.running = False
            if self.sound:
                self.sound.stop()
            if self.session_seconds > 0:
                self.save_session()
        self.update_timer_ui()

    def reset_timer(self, instance):
        self.running = False
        self.time_seconds = 0
        self.session_seconds = 0
        self.timer_label.text = '00:00:00'
        self.update_timer_ui()

    def update_timer(self, dt):
        if self.running:
            self.time_seconds += 1
            self.session_seconds += 1
            hours = self.time_seconds // 3600
            minutes = (self.time_seconds % 3600) // 60
            seconds = self.time_seconds % 60
            self.timer_label.text = f'{hours:02d}:{minutes:02d}:{seconds:02d}'

    def save_session(self):
        if self.session_seconds <= 0:
            return
        data = load_user_data()
        session = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'duration_seconds': self.session_seconds
        }
        data['history'].append(session)
        save_user_data(data)
        self.session_seconds = 0

    def apply_language(self):
        self.update_timer_ui()
        self.history_btn.text = get_text('history')
        self.zh_btn.text = get_text('lang_zh')
        self.en_btn.text = get_text('lang_en')

        if self.sound and self.sound.state == 'play':
            self.noise_toggle.text = get_text('white_noise_off')
        else:
            self.noise_toggle.text = get_text('white_noise_on')

        self.switch_noise_btn.text = get_text('switch_noise')

    def update_timer_ui(self):
        if self.running:
            self.start_btn.text = get_text('pause')
            self.status_label.text = get_text('focusing')
        else:
            self.start_btn.text = get_text('resume') if self.time_seconds > 0 else get_text('start')
            self.status_label.text = get_text('paused') if self.time_seconds > 0 else get_text('ready_focus')
        self.reset_btn.text = get_text('reset')

    def go_to_history(self, instance):
        self.manager.current = 'history'

# ---------- 歷史記錄畫面 ----------
class HistoryScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=20, spacing=15)

        self.title_label = Label(
            text='',
            font_size=44,
            bold=True,
            size_hint=(1, 0.2),
            color=(1,1,1,1),
            outline_width=2,
            outline_color=(0,0,0,1)
        )
        layout.add_widget(self.title_label)

        self.total_label = Label(
            text='',
            font_size=30,
            bold=True,
            size_hint=(1, 0.2),
            color=(1,1,1,1),
            outline_width=1,
            outline_color=(0,0,0,1)
        )
        layout.add_widget(self.total_label)

        self.scroll = ScrollView(size_hint=(1, 0.5))
        self.history_box = GridLayout(cols=1, spacing=5, size_hint_y=None)
        self.history_box.bind(minimum_height=self.history_box.setter('height'))
        self.scroll.add_widget(self.history_box)
        layout.add_widget(self.scroll)

        self.back_btn = FlatButton(text='', font_size=30, size_hint=(1, 0.2))
        self.back_btn.bind(on_press=lambda x: setattr(self.manager, 'current', 'timer'))
        layout.add_widget(self.back_btn)

        self.add_widget(layout)
        self.apply_language()

    def apply_language(self):
        self.title_label.text = get_text('history_title')
        self.back_btn.text = get_text('return_timer')
        self.refresh_history()

    def refresh_history(self):
        self.history_box.clear_widgets()
        data = load_user_data()
        history = data.get('history', [])
        total_seconds = sum(item['duration_seconds'] for item in history)
        self.total_label.text = get_text('total_focus') + format_duration(total_seconds)

        if not history:
            no_label = Label(
                text=get_text('no_history'),
                font_size=24,
                bold=True,
                size_hint_y=None,
                height=50,
                color=(1,1,1,1),
                outline_width=1,
                outline_color=(0,0,0,1)
            )
            self.history_box.add_widget(no_label)
        else:
            for item in reversed(history):
                timestamp = item['timestamp']
                duration = item['duration_seconds']
                duration_str = format_duration(duration)
                text = get_text('session_format').format(date=timestamp, duration=duration_str)
                label = Label(
                    text=text,
                    font_size=20,
                    bold=True,
                    size_hint_y=None,
                    height=40,
                    color=(1,1,1,1),
                    outline_width=1,
                    outline_color=(0,0,0,1)
                )
                self.history_box.add_widget(label)

    def on_enter(self):
        self.refresh_history()

# ---------- 應用主類 ----------
class FocusPodsApp(App):
    def build(self):
        # 請求 Android 通知權限
        try:
            from android.permissions import request_permissions, Permission
            request_permissions([Permission.POST_NOTIFICATIONS])
        except:
            pass

        data = load_user_data()
        global current_lang
        current_lang = data.get('language', 'zh')

        self.sm = ScreenManager()
        self.sm.add_widget(TimerScreen(name='timer'))
        self.sm.add_widget(HistoryScreen(name='history'))

        root = FloatLayout()
        background = BackgroundWidget(size_hint=(1, 1))
        root.add_widget(background)
        root.add_widget(self.sm)
        return root

    def set_language(self, lang):
        global current_lang
        current_lang = lang
        data = load_user_data()
        data['language'] = lang
        save_user_data(data)
        for screen in self.sm.screens:
            screen.apply_language()

    def on_pause(self):
        timer_screen = self.sm.get_screen('timer')
        if timer_screen.running:
            timer_screen.running = False
            timer_screen.update_timer_ui()
            if timer_screen.sound:
                timer_screen.sound.stop()
            timer_screen.save_session()
        return True

    def on_resume(self):
        timer_screen = self.sm.get_screen('timer')
        if not timer_screen.running:
            popup_content = Label(
                text=get_text('popup_welcome_msg'),
                font_size=20,
                bold=True
            )
            popup = Popup(
                title=get_text('popup_welcome_title'),
                content=popup_content,
                size_hint=(0.7, 0.4)
            )
            popup.open()
        return True

if __name__ == '__main__':
    FocusPodsApp().run()