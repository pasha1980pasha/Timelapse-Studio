import cv2
import os
import time
from datetime import datetime
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser
import threading
import numpy as np
from PIL import Image, ImageTk, ImageFont, ImageDraw
import json

class TimestampSettingsWindow:
    """Окно настроек таймпасов"""
    def __init__(self, parent):
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("Настройки таймпасов")
        self.window.geometry("500x700")
        self.window.configure(bg='#f0f0f0')
        
        # Настройки по умолчанию
        self.settings = {
            'enabled': True,
            'format': '%Y-%m-%d %H:%M:%S',
            'font_size': 30,
            'font_color': '#00FF00',
            'bg_color': '#000000',
            'bg_opacity': 0,
            'position': 'top-left',
            'margin_x': 10,
            'margin_y': 10,
            'shadow': True,
            'shadow_color': '#000000',
            'shadow_offset': 2,
            'show_milliseconds': False,
            'custom_text': '',
            'text_before_time': '',
            'text_after_time': ''
        }
        
        self.load_settings()
        self.create_widgets()
        
    def load_settings(self):
        """Загрузить настройки из файла"""
        try:
            if os.path.exists('timestamp_settings.json'):
                with open('timestamp_settings.json', 'r', encoding='utf-8') as f:
                    saved = json.load(f)
                    self.settings.update(saved)
        except:
            pass
    
    def save_settings(self):
        """Сохранить настройки в файл"""
        try:
            with open('timestamp_settings.json', 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=2)
        except:
            pass
    
    def create_widgets(self):
        # Заголовок
        title = tk.Label(self.window, text="⏰ Настройки таймпасов", 
                        font=("Arial", 16, "bold"), bg='#f0f0f0')
        title.pack(pady=10)
        
        # Фрейм для настроек
        frame = tk.Frame(self.window, bg='#f0f0f0')
        frame.pack(padx=20, pady=10, fill="both")
        
        row = 0
        
        # Включение таймпасов
        self.enabled_var = tk.BooleanVar(value=self.settings['enabled'])
        tk.Checkbutton(frame, text="Включить таймпасы", variable=self.enabled_var,
                      command=self.toggle_settings, bg='#f0f0f0').grid(row=row, column=0, columnspan=2, sticky="w", pady=5)
        row += 1
        
        # Формат времени
        tk.Label(frame, text="Формат времени:", bg='#f0f0f0').grid(row=row, column=0, sticky="w", pady=5)
        
        format_frame = tk.Frame(frame, bg='#f0f0f0')
        format_frame.grid(row=row, column=1, pady=5, sticky="w")
        
        self.format_var = tk.StringVar(value=self.settings['format'])
        formats = [
            ('ГГГГ-ММ-ДД ЧЧ:ММ:СС', '%Y-%m-%d %H:%M:%S'),
            ('ДД.ММ.ГГГГ ЧЧ:ММ:СС', '%d.%m.%Y %H:%M:%S'),
            ('ЧЧ:ММ:СС', '%H:%M:%S'),
            ('ЧЧ:ММ:СС.мс', '%H:%M:%S.%f')[:-3],
            ('Полная дата', '%A, %d %B %Y %H:%M:%S'),
            ('Только дата', '%Y-%m-%d'),
            ('Только время', '%H:%M:%S')
        ]
        
        for i, (display, fmt) in enumerate(formats):
            rb = tk.Radiobutton(format_frame, text=display, variable=self.format_var, 
                               value=fmt, bg='#f0f0f0')
            rb.pack(anchor="w")
        
        row += 1
        
        # Показывать миллисекунды
        self.ms_var = tk.BooleanVar(value=self.settings['show_milliseconds'])
        tk.Checkbutton(frame, text="Показывать миллисекунды", variable=self.ms_var,
                      bg='#f0f0f0').grid(row=row, column=0, columnspan=2, sticky="w", pady=5)
        row += 1
        
        # Дополнительный текст
        tk.Label(frame, text="Текст перед временем:", bg='#f0f0f0').grid(row=row, column=0, sticky="w", pady=5)
        self.text_before_var = tk.StringVar(value=self.settings['text_before_time'])
        tk.Entry(frame, textvariable=self.text_before_var, width=30).grid(row=row, column=1, pady=5)
        row += 1
        
        tk.Label(frame, text="Текст после времени:", bg='#f0f0f0').grid(row=row, column=0, sticky="w", pady=5)
        self.text_after_var = tk.StringVar(value=self.settings['text_after_time'])
        tk.Entry(frame, textvariable=self.text_after_var, width=30).grid(row=row, column=1, pady=5)
        row += 1
        
        # Размер шрифта
        tk.Label(frame, text="Размер шрифта:", bg='#f0f0f0').grid(row=row, column=0, sticky="w", pady=5)
        self.font_size_var = tk.IntVar(value=self.settings['font_size'])
        tk.Scale(frame, from_=10, to=100, variable=self.font_size_var, orient="horizontal",
                length=200, bg='#f0f0f0').grid(row=row, column=1, pady=5)
        row += 1
        
        # Цвет шрифта
        tk.Label(frame, text="Цвет текста:", bg='#f0f0f0').grid(row=row, column=0, sticky="w", pady=5)
        self.font_color_var = tk.StringVar(value=self.settings['font_color'])
        color_frame = tk.Frame(frame, bg='#f0f0f0')
        color_frame.grid(row=row, column=1, pady=5, sticky="w")
        
        tk.Entry(color_frame, textvariable=self.font_color_var, width=10).pack(side="left", padx=(0, 5))
        tk.Button(color_frame, text="Выбрать", command=self.choose_font_color).pack(side="left")
        
        # Показать цвет
        self.font_color_display = tk.Label(color_frame, text="   ", bg=self.font_color_var.get())
        self.font_color_display.pack(side="left", padx=5)
        row += 1
        
        # Позиция
        tk.Label(frame, text="Позиция на экране:", bg='#f0f0f0').grid(row=row, column=0, sticky="w", pady=5)
        self.position_var = tk.StringVar(value=self.settings['position'])
        position_combo = ttk.Combobox(frame, textvariable=self.position_var, width=27,
                                     values=['top-left', 'top-right', 'bottom-left', 'bottom-right',
                                             'top-center', 'bottom-center', 'center'])
        position_combo.grid(row=row, column=1, pady=5)
        row += 1
        
        # Отступы
        tk.Label(frame, text="Отступ по X:", bg='#f0f0f0').grid(row=row, column=0, sticky="w", pady=5)
        self.margin_x_var = tk.IntVar(value=self.settings['margin_x'])
        tk.Scale(frame, from_=0, to=100, variable=self.margin_x_var, orient="horizontal",
                length=200, bg='#f0f0f0').grid(row=row, column=1, pady=5)
        row += 1
        
        tk.Label(frame, text="Отступ по Y:", bg='#f0f0f0').grid(row=row, column=0, sticky="w", pady=5)
        self.margin_y_var = tk.IntVar(value=self.settings['margin_y'])
        tk.Scale(frame, from_=0, to=100, variable=self.margin_y_var, orient="horizontal",
                length=200, bg='#f0f0f0').grid(row=row, column=1, pady=5)
        row += 1
        
        # Тень
        self.shadow_var = tk.BooleanVar(value=self.settings['shadow'])
        tk.Checkbutton(frame, text="Добавить тень к тексту", variable=self.shadow_var,
                      bg='#f0f0f0').grid(row=row, column=0, columnspan=2, sticky="w", pady=5)
        row += 1
        
        # Кнопки
        button_frame = tk.Frame(frame, bg='#f0f0f0')
        button_frame.grid(row=row, column=0, columnspan=2, pady=20)
        
        tk.Button(button_frame, text="✅ Применить", command=self.apply_settings,
                 bg='#4CAF50', fg='white', padx=20).pack(side="left", padx=5)
        tk.Button(button_frame, text="❌ Отмена", command=self.window.destroy,
                 bg='#f44336', fg='white', padx=20).pack(side="left", padx=5)
        tk.Button(button_frame, text="👁️ Предпросмотр", command=self.show_preview,
                 bg='#2196F3', fg='white', padx=20).pack(side="left", padx=5)
        
        self.update_widgets_state()
    
    def toggle_settings(self):
        """Включить/выключить настройки"""
        self.update_widgets_state()
    
    def update_widgets_state(self):
        """Обновить состояние виджетов"""
        state = 'normal' if self.enabled_var.get() else 'disabled'
        
        for widget in self.window.winfo_children():
            if widget not in [self.enabled_var._tkinterVar] and hasattr(widget, 'configure'):
                try:
                    widget.configure(state=state)
                except:
                    pass
    
    def choose_font_color(self):
        """Выбрать цвет шрифта"""
        color = colorchooser.askcolor(title="Выберите цвет текста", 
                                      initialcolor=self.font_color_var.get())
        if color[1]:
            self.font_color_var.set(color[1])
            self.font_color_display.config(bg=color[1])
    
    def apply_settings(self):
        """Применить настройки"""
        self.settings.update({
            'enabled': self.enabled_var.get(),
            'format': self.format_var.get(),
            'font_size': self.font_size_var.get(),
            'font_color': self.font_color_var.get(),
            'position': self.position_var.get(),
            'margin_x': self.margin_x_var.get(),
            'margin_y': self.margin_y_var.get(),
            'shadow': self.shadow_var.get(),
            'show_milliseconds': self.ms_var.get(),
            'text_before_time': self.text_before_var.get(),
            'text_after_time': self.text_after_var.get()
        })
        
        self.save_settings()
        messagebox.showinfo("Сохранено", "Настройки таймпасов сохранены!")
        self.window.destroy()
    
    def show_preview(self):
        """Показать предпросмотр таймпаса"""
        preview_window = tk.Toplevel(self.window)
        preview_window.title("Предпросмотр таймпаса")
        preview_window.geometry("400x300")
        
        # Создаем изображение для предпросмотра
        preview_canvas = tk.Canvas(preview_window, width=400, height=300, bg='gray')
        preview_canvas.pack()
        
        # Генерируем текст таймпаса
        if self.ms_var.get():
            time_str = datetime.now().strftime('%H:%M:%S.%f')[:-3]
        else:
            time_str = datetime.now().strftime(self.format_var.get())
        
        full_text = f"{self.text_before_var.get()} {time_str} {self.text_after_var.get()}".strip()
        
        # Определяем позицию
        position = self.position_var.get()
        if position == 'top-left':
            x, y = self.margin_x_var.get() + 10, self.margin_y_var.get() + 10
        elif position == 'top-right':
            x = 400 - self.margin_x_var.get() - 10
            y = self.margin_y_var.get() + 10
        elif position == 'bottom-left':
            x = self.margin_x_var.get() + 10
            y = 300 - self.margin_y_var.get() - 10
        elif position == 'bottom-right':
            x = 400 - self.margin_x_var.get() - 10
            y = 300 - self.margin_y_var.get() - 10
        elif position == 'top-center':
            x = 200
            y = self.margin_y_var.get() + 10
        elif position == 'bottom-center':
            x = 200
            y = 300 - self.margin_y_var.get() - 10
        else:  # center
            x, y = 200, 150
        
        # Рисуем текст
        font_size = self.font_size_var.get()
        
        if self.shadow_var.get():
            preview_canvas.create_text(x+2, y+2, text=full_text, 
                                      fill='black',
                                      font=('Arial', font_size))
        
        preview_canvas.create_text(x, y, text=full_text, 
                                  fill=self.font_color_var.get(),
                                  font=('Arial', font_size))
        
        tk.Button(preview_window, text="Закрыть", command=preview_window.destroy).pack(pady=10)
    
    def get_settings(self):
        """Получить текущие настройки"""
        return self.settings

class WebcamRecorderWithTimestamps:
    """Веб-камера с расширенными таймпасами"""
    def __init__(self, root):
        self.root = root
        self.root.title("Webcam Recorder with Timestamps")
        self.root.geometry("1000x700")
        
        # Настройки таймпасов
        self.timestamp_settings = self.load_timestamp_settings()
        
        # Состояние
        self.is_recording = False
        self.is_timelapse = False
        self.video_writer = None
        self.cap = None
        self.frame_count = 0
        self.screenshot_count = 0
        self.timelapse_count = 0
        
        # Создаем GUI
        self.create_gui()
        
        # Инициализируем камеру
        self.init_camera()
        
        # Запускаем обновление видео
        self.update_video()
    
    def load_timestamp_settings(self):
        """Загрузить настройки таймпасов"""
        default_settings = {
            'enabled': True,
            'format': '%Y-%m-%d %H:%M:%S',
            'font_size': 30,
            'font_color': (0, 255, 0),  # BGR зеленый
            'bg_color': (0, 0, 0),
            'bg_opacity': 0,
            'position': 'top-left',
            'margin_x': 10,
            'margin_y': 10,
            'shadow': True,
            'shadow_color': (0, 0, 0),
            'shadow_offset': 2,
            'show_milliseconds': False,
            'text_before_time': '',
            'text_after_time': ''
        }
        
        try:
            if os.path.exists('timestamp_settings.json'):
                with open('timestamp_settings.json', 'r', encoding='utf-8') as f:
                    saved = json.load(f)
                    # Конвертируем цвет из строки в BGR
                    if 'font_color' in saved:
                        hex_color = saved['font_color'].lstrip('#')
                        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
                        saved['font_color'] = (rgb[2], rgb[1], rgb[0])  # RGB to BGR
                    default_settings.update(saved)
        except:
            pass
        
        return default_settings
    
    def create_gui(self):
        # Главный фрейм
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Левая панель - видео
        video_frame = tk.LabelFrame(main_frame, text="Видео с таймпасами", font=("Arial", 12))
        video_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        self.video_label = tk.Label(video_frame, bg='black')
        self.video_label.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Правая панель - управление
        control_frame = tk.LabelFrame(main_frame, text="Управление", font=("Arial", 12), width=300)
        control_frame.pack(side="right", fill="y")
        control_frame.pack_propagate(False)
        
        # Кнопки управления
        button_frame = tk.Frame(control_frame)
        button_frame.pack(pady=10, padx=10, fill="x")
        
        tk.Button(button_frame, text="⏰ Настроить таймпасы", command=self.open_timestamp_settings,
                 font=("Arial", 11), bg='#3498db', fg='white', height=2).pack(fill="x", pady=5)
        
        tk.Button(button_frame, text="⏺️ Начать запись", command=self.toggle_recording,
                 font=("Arial", 11), bg='#e74c3c', fg='white', height=2).pack(fill="x", pady=5)
        
        tk.Button(button_frame, text="📸 Сделать скриншот", command=self.take_screenshot,
                 font=("Arial", 11), bg='#2ecc71', fg='white', height=2).pack(fill="x", pady=5)
        
        tk.Button(button_frame, text="⏱️ Таймлапс (5 сек)", command=self.toggle_timelapse,
                 font=("Arial", 11), bg='#9b59b6', fg='white', height=2).pack(fill="x", pady=5)
        
        # Статус
        status_frame = tk.Frame(control_frame)
        status_frame.pack(pady=20, padx=10, fill="x")
        
        self.status_label = tk.Label(status_frame, text="Готов к работе", font=("Arial", 10))
        self.status_label.pack()
        
        # Счетчики
        counters_frame = tk.Frame(control_frame)
        counters_frame.pack(pady=10, padx=10, fill="x")
        
        self.video_counter = tk.Label(counters_frame, text="Видео: 0 кадров", font=("Arial", 9))
        self.video_counter.pack(anchor="w")
        
        self.screenshot_counter = tk.Label(counters_frame, text="Скриншоты: 0", font=("Arial", 9))
        self.screenshot_counter.pack(anchor="w")
        
        self.timelapse_counter = tk.Label(counters_frame, text="Таймлапс: 0", font=("Arial", 9))
        self.timelapse_counter.pack(anchor="w")
        
        # Информация о таймпасе
        timestamp_info_frame = tk.LabelFrame(control_frame, text="Текущий таймпас", font=("Arial", 10))
        timestamp_info_frame.pack(pady=10, padx=10, fill="x")
        
        self.timestamp_preview = tk.Label(timestamp_info_frame, text="", font=("Courier", 9), bg='black', fg='white')
        self.timestamp_preview.pack(padx=5, pady=5, fill="x")
        
        # Кнопки управления папками
        folder_frame = tk.Frame(control_frame)
        folder_frame.pack(pady=10, padx=10, fill="x")
        
        tk.Button(folder_frame, text="📁 Папка видео", command=lambda: self.open_folder('videos'),
                 font=("Arial", 9)).pack(fill="x", pady=2)
        
        tk.Button(folder_frame, text="📁 Папка скриншотов", command=lambda: self.open_folder('screenshots'),
                 font=("Arial", 9)).pack(fill="x", pady=2)
        
        # Выход
        tk.Button(control_frame, text="🚪 Выход", command=self.exit_app,
                 font=("Arial", 11), bg='#34495e', fg='white', height=2).pack(side="bottom", fill="x", pady=10, padx=10)
    
    def init_camera(self):
        """Инициализировать камеру"""
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            messagebox.showerror("Ошибка", "Не удалось подключиться к камере!")
            self.root.quit()
            return
        
        # Устанавливаем разрешение
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    
    def add_timestamp_to_frame(self, frame):
        """Добавить таймпас на кадр"""
        if not self.timestamp_settings['enabled']:
            return frame
        
        height, width = frame.shape[:2]
        
        # Получаем текст таймпаса
        if self.timestamp_settings['show_milliseconds']:
            time_str = datetime.now().strftime('%H:%M:%S.%f')[:-3]
        else:
            time_str = datetime.now().strftime(self.timestamp_settings['format'])
        
        # Добавляем пользовательский текст
        text_before = self.timestamp_settings['text_before_time']
        text_after = self.timestamp_settings['text_after_time']
        full_text = f"{text_before} {time_str} {text_after}".strip()
        
        # Обновляем предпросмотр в GUI
        self.timestamp_preview.config(text=full_text)
        
        # Определяем позицию
        position = self.timestamp_settings['position']
        margin_x = self.timestamp_settings['margin_x']
        margin_y = self.timestamp_settings['margin_y']
        font_size = self.timestamp_settings['font_size']
        
        # Вычисляем размер текста
        text_size = cv2.getTextSize(full_text, cv2.FONT_HERSHEY_SIMPLEX, font_size/30, 2)[0]
        text_width, text_height = text_size
        
        if position == 'top-left':
            x, y = margin_x, margin_y + text_height
        elif position == 'top-right':
            x = width - text_width - margin_x
            y = margin_y + text_height
        elif position == 'bottom-left':
            x = margin_x
            y = height - margin_y
        elif position == 'bottom-right':
            x = width - text_width - margin_x
            y = height - margin_y
        elif position == 'top-center':
            x = (width - text_width) // 2
            y = margin_y + text_height
        elif position == 'bottom-center':
            x = (width - text_width) // 2
            y = height - margin_y
        else:  # center
            x = (width - text_width) // 2
            y = (height + text_height) // 2
        
        # Добавляем тень если нужно
        if self.timestamp_settings['shadow']:
            shadow_offset = self.timestamp_settings['shadow_offset']
            shadow_color = self.timestamp_settings['shadow_color']
            cv2.putText(frame, full_text, (x + shadow_offset, y + shadow_offset),
                       cv2.FONT_HERSHEY_SIMPLEX, font_size/30, shadow_color, 2)
        
        # Добавляем основной текст
        font_color = self.timestamp_settings['font_color']
        cv2.putText(frame, full_text, (x, y),
                   cv2.FONT_HERSHEY_SIMPLEX, font_size/30, font_color, 2)
        
        return frame
    
    def update_video(self):
        """Обновить видео-поток"""
        if self.cap:
            ret, frame = self.cap.read()
            if ret:
                # Зеркально отражаем
                frame = cv2.flip(frame, 1)
                
                # Добавляем таймпас
                frame = self.add_timestamp_to_frame(frame)
                
                # Конвертируем для Tkinter
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Масштабируем для отображения
                display_width = 640
                display_height = 480
                rgb_frame = cv2.resize(rgb_frame, (display_width, display_height))
                
                # Конвертируем в фотоизображение Tkinter
                img = Image.fromarray(rgb_frame)
                imgtk = ImageTk.PhotoImage(image=img)
                
                # Обновляем изображение
                self.video_label.config(image=imgtk)
                self.video_label.image = imgtk
                
                # Если идет запись, сохраняем кадр
                if self.is_recording and self.video_writer:
                    # Для записи используем оригинальный размер с таймпасом
                    ret, record_frame = self.cap.read()
                    if ret:
                        record_frame = cv2.flip(record_frame, 1)
                        record_frame = self.add_timestamp_to_frame(record_frame)
                        self.video_writer.write(record_frame)
                        self.frame_count += 1
                        self.video_counter.config(text=f"Видео: {self.frame_count} кадров")
        
        # Планируем следующее обновление
        self.root.after(30, self.update_video)
    
    def open_timestamp_settings(self):
        """Открыть настройки таймпасов"""
        settings_window = TimestampSettingsWindow(self.root)
        self.root.wait_window(settings_window.window)
        
        # Обновляем настройки
        self.timestamp_settings = self.load_timestamp_settings()
        self.status_label.config(text="Настройки таймпасов обновлены")
    
    def toggle_recording(self):
        """Переключить запись видео"""
        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_recording()
    
    def start_recording(self):
        """Начать запись видео"""
        # Создаем папку если нужно
        if not os.path.exists('videos'):
            os.makedirs('videos')
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"recording_{timestamp}.avi"
        filepath = os.path.join('videos', filename)
        
        # Получаем размер кадра
        width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # Создаем VideoWriter
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        self.video_writer = cv2.VideoWriter(filepath, fourcc, 20.0, (width, height))
        
        if not self.video_writer.isOpened():
            messagebox.showerror("Ошибка", "Не удалось создать файл записи!")
            return
        
        self.is_recording = True
        self.frame_count = 0
        self.status_label.config(text="🔴 Идет запись...", fg='red')
        
        print(f"[RECORDING] Запись начата: {filename}")
    
    def stop_recording(self):
        """Остановить запись видео"""
        if self.is_recording and self.video_writer:
            self.video_writer.release()
            self.video_writer = None
            self.is_recording = False
            
            self.status_label.config(text="✅ Запись сохранена", fg='green')
            print(f"[RECORDING] Запись остановлена. Кадров: {self.frame_count}")
    
    def take_screenshot(self):
        """Сделать скриншот"""
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.flip(frame, 1)
            
            # Добавляем таймпас
            frame = self.add_timestamp_to_frame(frame)
            
            # Создаем папку если нужно
            if not os.path.exists('screenshots'):
                os.makedirs('screenshots')
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
            filename = f"screenshot_{timestamp}.jpg"
            filepath = os.path.join('screenshots', filename)
            
            # Сохраняем
            cv2.imwrite(filepath, frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
            
            self.screenshot_count += 1
            self.screenshot_counter.config(text=f"Скриншоты: {self.screenshot_count}")
            
            self.status_label.config(text=f"📸 Скриншот сохранен!", fg='blue')
            self.root.after(2000, lambda: self.status_label.config(text="Готов к работе", fg='black'))
            
            print(f"[SCREENSHOT] Сохранен: {filename}")
    
    def toggle_timelapse(self):
        """Переключить таймлапс"""
        if not self.is_timelapse:
            self.start_timelapse()
        else:
            self.stop_timelapse()
    
    def start_timelapse(self):
        """Начать таймлапс"""
        self.is_timelapse = True
        self.timelapse_count = 0
        
        # Запускаем поток таймлапса
        self.timelapse_thread = threading.Thread(target=self.timelapse_worker, daemon=True)
        self.timelapse_thread.start()
        
        self.status_label.config(text="🔵 Таймлапс активен", fg='purple')
        print(f"[TIMELAPSE] Таймлапс начат")
    
    def stop_timelapse(self):
        """Остановить таймлапс"""
        self.is_timelapse = False
        
        self.status_label.config(text=f"✅ Таймлапс сохранен ({self.timelapse_count} кадров)", fg='green')
        print(f"[TIMELAPSE] Остановлен. Кадров: {self.timelapse_count}")
    
    def timelapse_worker(self):
        """Рабочий поток для таймлапса"""
        last_capture = 0
        
        while self.is_timelapse:
            current_time = time.time()
            
            # Интервал 5 секунд
            if current_time - last_capture >= 5:
                # Делаем скриншот
                ret, frame = self.cap.read()
                if ret:
                    frame = cv2.flip(frame, 1)
                    frame = self.add_timestamp_to_frame(frame)
                    
                    if not os.path.exists('screenshots'):
                        os.makedirs('screenshots')
                    
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
                    filename = f"timelapse_{timestamp}.jpg"
                    filepath = os.path.join('screenshots', filename)
                    
                    cv2.imwrite(filepath, frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
                    
                    self.timelapse_count += 1
                    self.timelapse_counter.config(text=f"Таймлапс: {self.timelapse_count}")
                    
                    print(f"[TIMELAPSE] Кадр {self.timelapse_count} сохранен")
                
                last_capture = current_time
            
            time.sleep(0.1)
    
    def open_folder(self, folder_type):
        """Открыть папку"""
        if folder_type == 'videos':
            folder = 'videos'
        else:
            folder = 'screenshots'
        
        if not os.path.exists(folder):
            os.makedirs(folder)
        
        try:
            os.startfile(folder)
        except:
            messagebox.showinfo("Папка", f"Файлы в папке: {folder}")
    
    def exit_app(self):
        """Выйти из приложения"""
        if self.is_recording:
            self.stop_recording()
        
        if self.is_timelapse:
            self.stop_timelapse()
        
        if self.cap:
            self.cap.release()
        
        self.root.quit()

def main():
    root = tk.Tk()
    app = WebcamRecorderWithTimestamps(root)
    
    root.protocol("WM_DELETE_WINDOW", app.exit_app)
    root.mainloop()

if __name__ == "__main__":
    main()
