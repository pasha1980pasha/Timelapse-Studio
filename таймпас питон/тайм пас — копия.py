import cv2
import os
import time
from datetime import datetime
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import numpy as np

class SettingsWindow:
    """Окно настроек записи"""
    def __init__(self, parent):
        self.parent = parent
        self.window = tk.Toplevel(parent)
        self.window.title("Настройки записи")
        self.window.geometry("500x600")
        self.window.configure(bg='#f0f0f0')
        
        # Переменные настроек
        self.recording_dir = tk.StringVar(value="webcam_recordings")
        self.screenshots_dir = tk.StringVar(value="screenshots")
        self.fps = tk.IntVar(value=20)
        self.resolution = tk.StringVar(value="1280x720")
        self.timelapse_interval = tk.IntVar(value=5)
        self.video_format = tk.StringVar(value="avi")
        self.image_format = tk.StringVar(value="jpg")
        self.add_timestamp = tk.BooleanVar(value=True)
        self.show_overlay = tk.BooleanVar(value=True)
        self.auto_start = tk.BooleanVar(value=False)
        
        self.create_widgets()
        self.load_last_settings()
        
    def create_widgets(self):
        # Заголовок
        title = tk.Label(self.window, text="⚙️ Настройки записи", 
                        font=("Arial", 16, "bold"), bg='#f0f0f0')
        title.pack(pady=10)
        
        # Фрейм для настроек
        frame = tk.Frame(self.window, bg='#f0f0f0')
        frame.pack(padx=20, pady=10, fill="both")
        
        row = 0
        
        # Папка для видео
        tk.Label(frame, text="Папка для видео:", bg='#f0f0f0').grid(row=row, column=0, sticky="w", pady=5)
        tk.Entry(frame, textvariable=self.recording_dir, width=30).grid(row=row, column=1, pady=5)
        tk.Button(frame, text="Обзор...", command=self.browse_recording_dir).grid(row=row, column=2, padx=5)
        row += 1
        
        # Папка для скриншотов
        tk.Label(frame, text="Папка для скриншотов:", bg='#f0f0f0').grid(row=row, column=0, sticky="w", pady=5)
        tk.Entry(frame, textvariable=self.screenshots_dir, width=30).grid(row=row, column=1, pady=5)
        tk.Button(frame, text="Обзор...", command=self.browse_screenshots_dir).grid(row=row, column=2, padx=5)
        row += 1
        
        # Разрешение
        tk.Label(frame, text="Разрешение:", bg='#f0f0f0').grid(row=row, column=0, sticky="w", pady=5)
        resolution_combo = ttk.Combobox(frame, textvariable=self.resolution, width=27,
                                       values=["640x480", "800x600", "1024x768", "1280x720", "1920x1080"])
        resolution_combo.grid(row=row, column=1, pady=5)
        row += 1
        
        # FPS
        tk.Label(frame, text="FPS записи:", bg='#f0f0f0').grid(row=row, column=0, sticky="w", pady=5)
        fps_scale = tk.Scale(frame, from_=5, to=60, variable=self.fps, orient="horizontal", 
                            length=200, bg='#f0f0f0')
        fps_scale.grid(row=row, column=1, pady=5)
        row += 1
        
        # Интервал таймлапса
        tk.Label(frame, text="Интервал таймлапса (сек):", bg='#f0f0f0').grid(row=row, column=0, sticky="w", pady=5)
        interval_scale = tk.Scale(frame, from_=1, to=60, variable=self.timelapse_interval, 
                                 orient="horizontal", length=200, bg='#f0f0f0')
        interval_scale.grid(row=row, column=1, pady=5)
        row += 1
        
        # Формат видео
        tk.Label(frame, text="Формат видео:", bg='#f0f0f0').grid(row=row, column=0, sticky="w", pady=5)
        ttk.Combobox(frame, textvariable=self.video_format, width=27,
                     values=["avi", "mp4", "mov"]).grid(row=row, column=1, pady=5)
        row += 1
        
        # Формат изображений
        tk.Label(frame, text="Формат скриншотов:", bg='#f0f0f0').grid(row=row, column=0, sticky="w", pady=5)
        ttk.Combobox(frame, textvariable=self.image_format, width=27,
                     values=["jpg", "png", "bmp"]).grid(row=row, column=1, pady=5)
        row += 1
        
        # Чекбоксы
        tk.Checkbutton(frame, text="Добавлять время на кадры", variable=self.add_timestamp, 
                      bg='#f0f0f0').grid(row=row, column=0, columnspan=2, sticky="w", pady=5)
        row += 1
        
        tk.Checkbutton(frame, text="Показывать оверлей с информацией", variable=self.show_overlay,
                      bg='#f0f0f0').grid(row=row, column=0, columnspan=2, sticky="w", pady=5)
        row += 1
        
        tk.Checkbutton(frame, text="Автозапуск при открытии", variable=self.auto_start,
                      bg='#f0f0f0').grid(row=row, column=0, columnspan=2, sticky="w", pady=5)
        row += 1
        
        # Кнопки
        button_frame = tk.Frame(frame, bg='#f0f0f0')
        button_frame.grid(row=row, column=0, columnspan=3, pady=20)
        
        tk.Button(button_frame, text="✅ Сохранить", command=self.save_settings,
                 bg='#4CAF50', fg='white', padx=20).pack(side="left", padx=5)
        tk.Button(button_frame, text="❌ Отмена", command=self.window.destroy,
                 bg='#f44336', fg='white', padx=20).pack(side="left", padx=5)
        tk.Button(button_frame, text="🔄 По умолчанию", command=self.reset_defaults,
                 bg='#2196F3', fg='white', padx=20).pack(side="left", padx=5)
    
    def browse_recording_dir(self):
        dir_path = filedialog.askdirectory(title="Выберите папку для видео")
        if dir_path:
            self.recording_dir.set(dir_path)
    
    def browse_screenshots_dir(self):
        dir_path = filedialog.askdirectory(title="Выберите папку для скриншотов")
        if dir_path:
            self.screenshots_dir.set(dir_path)
    
    def save_settings(self):
        # Создаем папки если не существуют
        for dir_path in [self.recording_dir.get(), self.screenshots_dir.get()]:
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
        
        # Сохраняем настройки в файл
        settings = {
            'recording_dir': self.recording_dir.get(),
            'screenshots_dir': self.screenshots_dir.get(),
            'fps': self.fps.get(),
            'resolution': self.resolution.get(),
            'timelapse_interval': self.timelapse_interval.get(),
            'video_format': self.video_format.get(),
            'image_format': self.image_format.get(),
            'add_timestamp': self.add_timestamp.get(),
            'show_overlay': self.show_overlay.get(),
            'auto_start': self.auto_start.get()
        }
        
        try:
            with open('webcam_settings.txt', 'w') as f:
                for key, value in settings.items():
                    f.write(f"{key}={value}\n")
            
            messagebox.showinfo("Сохранено", "Настройки успешно сохранены!")
            self.window.destroy()
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить настройки: {e}")
    
    def load_last_settings(self):
        try:
            if os.path.exists('webcam_settings.txt'):
                with open('webcam_settings.txt', 'r') as f:
                    for line in f:
                        if '=' in line:
                            key, value = line.strip().split('=', 1)
                            if key == 'recording_dir':
                                self.recording_dir.set(value)
                            elif key == 'screenshots_dir':
                                self.screenshots_dir.set(value)
                            elif key == 'fps':
                                self.fps.set(int(value))
                            elif key == 'resolution':
                                self.resolution.set(value)
                            elif key == 'timelapse_interval':
                                self.timelapse_interval.set(int(value))
                            elif key == 'video_format':
                                self.video_format.set(value)
                            elif key == 'image_format':
                                self.image_format.set(value)
                            elif key == 'add_timestamp':
                                self.add_timestamp.set(value.lower() == 'true')
                            elif key == 'show_overlay':
                                self.show_overlay.set(value.lower() == 'true')
                            elif key == 'auto_start':
                                self.auto_start.set(value.lower() == 'true')
        except:
            pass
    
    def reset_defaults(self):
        self.recording_dir.set("webcam_recordings")
        self.screenshots_dir.set("screenshots")
        self.fps.set(20)
        self.resolution.set("1280x720")
        self.timelapse_interval.set(5)
        self.video_format.set("avi")
        self.image_format.set("jpg")
        self.add_timestamp.set(True)
        self.show_overlay.set(True)
        self.auto_start.set(False)
    
    def get_settings(self):
        return {
            'recording_dir': self.recording_dir.get(),
            'screenshots_dir': self.screenshots_dir.get(),
            'fps': self.fps.get(),
            'resolution': tuple(map(int, self.resolution.get().split('x'))),
            'timelapse_interval': self.timelapse_interval.get(),
            'video_format': self.video_format.get(),
            'image_format': self.image_format.get(),
            'add_timestamp': self.add_timestamp.get(),
            'show_overlay': self.show_overlay.get(),
            'auto_start': self.auto_start.get()
        }

class ControlPanel:
    """Панель управления записью"""
    def __init__(self, parent, app):
        self.app = app
        self.frame = tk.Frame(parent, bg='#2c3e50')
        self.frame.pack(fill="x", padx=10, pady=10)
        
        self.create_widgets()
    
    def create_widgets(self):
        # Статус
        self.status_label = tk.Label(self.frame, text="📹 Готов к работе", 
                                    font=("Arial", 12), bg='#2c3e50', fg='white')
        self.status_label.grid(row=0, column=0, columnspan=4, pady=5, sticky="w")
        
        # Счетчики
        self.counters_frame = tk.Frame(self.frame, bg='#2c3e50')
        self.counters_frame.grid(row=1, column=0, columnspan=4, pady=5)
        
        self.video_label = tk.Label(self.counters_frame, text="Видео: 0 кадров", 
                                   bg='#2c3e50', fg='#3498db')
        self.video_label.pack(side="left", padx=10)
        
        self.screenshot_label = tk.Label(self.counters_frame, text="Скриншоты: 0", 
                                        bg='#2c3e50', fg='#2ecc71')
        self.screenshot_label.pack(side="left", padx=10)
        
        self.timelapse_label = tk.Label(self.counters_frame, text="Таймлапс: 0", 
                                       bg='#2c3e50', fg='#e74c3c')
        self.timelapse_label.pack(side="left", padx=10)
        
        # Кнопки управления
        buttons_frame = tk.Frame(self.frame, bg='#2c3e50')
        buttons_frame.grid(row=2, column=0, columnspan=4, pady=10)
        
        # Кнопка записи видео
        self.record_btn = tk.Button(buttons_frame, text="⏺️ Начать запись", 
                                   command=self.toggle_recording,
                                   bg='#e74c3c', fg='white', font=("Arial", 10),
                                   width=15, height=2)
        self.record_btn.pack(side="left", padx=5)
        
        # Кнопка скриншота
        self.screenshot_btn = tk.Button(buttons_frame, text="📸 Скриншот", 
                                       command=self.take_screenshot,
                                       bg='#3498db', fg='white', font=("Arial", 10),
                                       width=15, height=2)
        self.screenshot_btn.pack(side="left", padx=5)
        
        # Кнопка таймлапса
        self.timelapse_btn = tk.Button(buttons_frame, text="⏱️ Таймлапс", 
                                      command=self.toggle_timelapse,
                                      bg='#9b59b6', fg='white', font=("Arial", 10),
                                      width=15, height=2)
        self.timelapse_btn.pack(side="left", padx=5)
        
        # Кнопка паузы
        self.pause_btn = tk.Button(buttons_frame, text="⏸️ Пауза", 
                                  command=self.toggle_pause,
                                  bg='#f39c12', fg='white', font=("Arial", 10),
                                  width=15, height=2)
        self.pause_btn.pack(side="left", padx=5)
    
    def toggle_recording(self):
        self.app.toggle_recording()
    
    def take_screenshot(self):
        self.app.take_screenshot()
    
    def toggle_timelapse(self):
        self.app.toggle_timelapse()
    
    def toggle_pause(self):
        self.app.toggle_pause()
    
    def update_status(self, text, color='white'):
        self.status_label.config(text=text, fg=color)
    
    def update_counters(self, video_frames=0, screenshots=0, timelapse=0):
        self.video_label.config(text=f"Видео: {video_frames} кадров")
        self.screenshot_label.config(text=f"Скриншоты: {screenshots}")
        self.timelapse_label.config(text=f"Таймлапс: {timelapse}")
    
    def update_record_button(self, is_recording):
        if is_recording:
            self.record_btn.config(text="⏹️ Стоп запись", bg='#c0392b')
        else:
            self.record_btn.config(text="⏺️ Начать запись", bg='#e74c3c')
    
    def update_timelapse_button(self, is_timelapse):
        if is_timelapse:
            self.timelapse_btn.config(text="⏹️ Стоп таймлапс", bg='#8e44ad')
        else:
            self.timelapse_btn.config(text="⏱️ Таймлапс", bg='#9b59b6')
    
    def update_pause_button(self, is_paused):
        if is_paused:
            self.pause_btn.config(text="▶️ Продолжить", bg='#27ae60')
        else:
            self.pause_btn.config(text="⏸️ Пауза", bg='#f39c12')

class WebcamRecorderApp:
    """Главное приложение веб-камеры"""
    def __init__(self, root):
        self.root = root
        self.root.title("Webcam Recorder Pro")
        self.root.geometry("900x700")
        self.root.configure(bg='#34495e')
        
        # Состояние
        self.is_recording = False
        self.is_timelapse = False
        self.is_paused = False
        self.video_writer = None
        self.timelapse_thread = None
        self.frame_count = 0
        self.screenshot_count = 0
        self.timelapse_count = 0
        self.recording_start = None
        self.timelapse_start = None
        self.cap = None
        
        # Загружаем настройки
        self.settings = self.load_settings()
        
        # Создаем интерфейс
        self.create_gui()
        
        # Запускаем камеру
        self.init_camera()
        
        # Запускаем обновление видео
        self.update_video()
    
    def load_settings(self):
        """Загрузить настройки из файла или использовать по умолчанию"""
        default_settings = {
            'recording_dir': 'webcam_recordings',
            'screenshots_dir': 'screenshots',
            'fps': 20,
            'resolution': (1280, 720),
            'timelapse_interval': 5,
            'video_format': 'avi',
            'image_format': 'jpg',
            'add_timestamp': True,
            'show_overlay': True,
            'auto_start': False
        }
        
        try:
            if os.path.exists('webcam_settings.txt'):
                with open('webcam_settings.txt', 'r') as f:
                    for line in f:
                        if '=' in line:
                            key, value = line.strip().split('=', 1)
                            if key == 'recording_dir':
                                default_settings['recording_dir'] = value
                            elif key == 'screenshots_dir':
                                default_settings['screenshots_dir'] = value
                            elif key == 'fps':
                                default_settings['fps'] = int(value)
                            elif key == 'resolution':
                                w, h = value.split('x')
                                default_settings['resolution'] = (int(w), int(h))
                            elif key == 'timelapse_interval':
                                default_settings['timelapse_interval'] = int(value)
                            elif key == 'video_format':
                                default_settings['video_format'] = value
                            elif key == 'image_format':
                                default_settings['image_format'] = value
                            elif key == 'add_timestamp':
                                default_settings['add_timestamp'] = value.lower() == 'true'
                            elif key == 'show_overlay':
                                default_settings['show_overlay'] = value.lower() == 'true'
                            elif key == 'auto_start':
                                default_settings['auto_start'] = value.lower() == 'true'
        except:
            pass
        
        # Создаем папки
        for dir_path in [default_settings['recording_dir'], default_settings['screenshots_dir']]:
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
        
        return default_settings
    
    def create_gui(self):
        # Заголовок
        header = tk.Frame(self.root, bg='#2c3e50', height=80)
        header.pack(fill="x")
        
        title = tk.Label(header, text="🎥 Webcam Recorder Pro", 
                        font=("Arial", 24, "bold"), bg='#2c3e50', fg='white')
        title.pack(pady=20)
        
        # Основной контент
        main_frame = tk.Frame(self.root, bg='#34495e')
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Левая панель - видео
        video_frame = tk.LabelFrame(main_frame, text="Видео", font=("Arial", 12),
                                   bg='#2c3e50', fg='white', padx=10, pady=10)
        video_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        self.video_label = tk.Label(video_frame, bg='black')
        self.video_label.pack(fill="both", expand=True)
        
        # Правая панель - управление
        control_frame = tk.LabelFrame(main_frame, text="Управление", font=("Arial", 12),
                                     bg='#2c3e50', fg='white', padx=10, pady=10, width=300)
        control_frame.pack(side="right", fill="y", padx=(10, 0))
        control_frame.pack_propagate(False)
        
        # Панель управления
        self.control_panel = ControlPanel(control_frame, self)
        
        # Кнопки настроек и выхода
        bottom_frame = tk.Frame(control_frame, bg='#2c3e50')
        bottom_frame.pack(side="bottom", fill="x", pady=20)
        
        tk.Button(bottom_frame, text="⚙️ Настройки", command=self.open_settings,
                 bg='#7f8c8d', fg='white', width=15).pack(side="left", padx=5)
        
        tk.Button(bottom_frame, text="📁 Открыть папку", command=self.open_folder,
                 bg='#16a085', fg='white', width=15).pack(side="left", padx=5)
        
        tk.Button(bottom_frame, text="🚪 Выход", command=self.exit_app,
                 bg='#e74c3c', fg='white', width=15).pack(side="left", padx=5)
        
        # Информация о времени
        self.time_label = tk.Label(control_frame, text="", font=("Arial", 10),
                                  bg='#2c3e50', fg='#ecf0f1')
        self.time_label.pack(pady=10)
    
    def init_camera(self):
        """Инициализировать камеру"""
        try:
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                messagebox.showerror("Ошибка", "Не удалось подключиться к камере!")
                self.root.quit()
                return
            
            # Устанавливаем разрешение
            width, height = self.settings['resolution']
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
            
            # Получаем реальное разрешение
            self.actual_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            self.actual_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            self.control_panel.update_status(f"✅ Камера готова ({self.actual_width}x{self.actual_height})", '#2ecc71')
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка инициализации камеры: {e}")
    
    def update_video(self):
        """Обновить видео-поток"""
        if self.cap and not self.is_paused:
            ret, frame = self.cap.read()
            if ret:
                # Зеркально отражаем
                frame = cv2.flip(frame, 1)
                
                # Добавляем оверлей если нужно
                if self.settings['show_overlay']:
                    frame = self.add_overlay(frame)
                
                # Конвертируем для Tkinter
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Масштабируем для отображения
                display_width = 640
                display_height = int(self.actual_height * (display_width / self.actual_width))
                rgb_frame = cv2.resize(rgb_frame, (display_width, display_height))
                
                # Конвертируем в фотоизображение Tkinter
                img = self.cv2_to_tkinter(rgb_frame)
                
                # Обновляем изображение
                self.video_label.config(image=img)
                self.video_label.image = img
                
                # Записываем если идет запись
                if self.is_recording and self.video_writer:
                    # Для записи используем оригинальный размер
                    ret, record_frame = self.cap.read()
                    if ret:
                        record_frame = cv2.flip(record_frame, 1)
                        if self.settings['add_timestamp']:
                            record_frame = self.add_timestamp_to_frame(record_frame)
                        self.video_writer.write(record_frame)
                        self.frame_count += 1
                        self.control_panel.update_counters(
                            video_frames=self.frame_count,
                            screenshots=self.screenshot_count,
                            timelapse=self.timelapse_count
                        )
        
        # Обновляем время
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.config(text=f"Текущее время: {current_time}")
        
        # Планируем следующее обновление
        self.root.after(30, self.update_video)
    
    def cv2_to_tkinter(self, frame):
        """Конвертировать кадр OpenCV для Tkinter"""
        from PIL import Image, ImageTk
        img = Image.fromarray(frame)
        imgtk = ImageTk.PhotoImage(image=img)
        return imgtk
    
    def add_overlay(self, frame):
        """Добавить оверлей с информацией"""
        height, width = frame.shape[:2]
        
        # Текущее время
        if self.settings['add_timestamp']:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cv2.putText(frame, current_time, (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Статус записи
        y_pos = 60
        if self.is_recording:
            cv2.putText(frame, "🔴 ЗАПИСЬ", (10, y_pos), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            y_pos += 35
            
            if self.recording_start:
                elapsed = datetime.now() - self.recording_start
                hours, remainder = divmod(elapsed.seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
                cv2.putText(frame, f"Время: {time_str}", (10, y_pos), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                y_pos += 30
                cv2.putText(frame, f"Кадры: {self.frame_count}", (10, y_pos), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                y_pos += 35
        
        # Статус таймлапса
        if self.is_timelapse:
            cv2.putText(frame, "🔵 ТАЙМЛАПС", (10, y_pos), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 100, 0), 2)
            y_pos += 30
            cv2.putText(frame, f"Кадров: {self.timelapse_count}", (10, y_pos), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 100, 0), 2)
            y_pos += 35
        
        # Информация
        cv2.putText(frame, f"Скриншотов: {self.screenshot_count}", 
                   (10, height - 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 200, 0), 2)
        
        return frame
    
    def add_timestamp_to_frame(self, frame):
        """Добавить только timestamp на кадр для записи"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cv2.putText(frame, current_time, (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        return frame
    
    def toggle_recording(self):
        """Переключить запись видео"""
        if not self.is_recording:
            self.start_recording()
        else:
            self.stop_recording()
    
    def start_recording(self):
        """Начать запись видео"""
        if self.is_paused:
            messagebox.showwarning("Пауза", "Сначала снимите с паузы!")
            return
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"recording_{timestamp}.{self.settings['video_format']}"
        filepath = os.path.join(self.settings['recording_dir'], filename)
        
        # Определяем кодек в зависимости от формата
        if self.settings['video_format'] == 'avi':
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
        elif self.settings['video_format'] == 'mp4':
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        else:
            fourcc = cv2.VideoWriter_fourcc(*'MJPG')
        
        self.video_writer = cv2.VideoWriter(
            filepath,
            fourcc,
            self.settings['fps'],
            (self.actual_width, self.actual_height)
        )
        
        if not self.video_writer.isOpened():
            messagebox.showerror("Ошибка", "Не удалось создать файл записи!")
            return
        
        self.is_recording = True
        self.recording_start = datetime.now()
        self.frame_count = 0
        
        self.control_panel.update_status("🔴 Идет запись видео...", '#e74c3c')
        self.control_panel.update_record_button(True)
        
        print(f"[RECORDING] Начата запись: {filename}")
    
    def stop_recording(self):
        """Остановить запись видео"""
        if self.is_recording and self.video_writer:
            self.video_writer.release()
            self.video_writer = None
            self.is_recording = False
            
            if self.recording_start:
                duration = datetime.now() - self.recording_start
                hours, remainder = divmod(duration.seconds, 3600)
                minutes, seconds = divmod(remainder, 60)
                
                self.control_panel.update_status(
                    f"✅ Запись сохранена ({hours:02d}:{minutes:02d}:{seconds:02d})", 
                    '#2ecc71'
                )
                
                print(f"[RECORDING] Запись остановлена. Длительность: {hours:02d}:{minutes:02d}:{seconds:02d}")
            
            self.control_panel.update_record_button(False)
    
    def take_screenshot(self):
        """Сделать скриншот"""
        if self.is_paused:
            messagebox.showwarning("Пауза", "Сначала снимите с паузы!")
            return
        
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.flip(frame, 1)
            
            # Добавляем timestamp если нужно
            if self.settings['add_timestamp']:
                frame = self.add_timestamp_to_frame(frame)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
            filename = f"screenshot_{timestamp}.{self.settings['image_format']}"
            filepath = os.path.join(self.settings['screenshots_dir'], filename)
            
            # Сохраняем в зависимости от формата
            if self.settings['image_format'] == 'jpg':
                cv2.imwrite(filepath, frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
            elif self.settings['image_format'] == 'png':
                cv2.imwrite(filepath, frame, [cv2.IMWRITE_PNG_COMPRESSION, 3])
            else:
                cv2.imwrite(filepath, frame)
            
            self.screenshot_count += 1
            self.control_panel.update_counters(
                video_frames=self.frame_count,
                screenshots=self.screenshot_count,
                timelapse=self.timelapse_count
            )
            
            print(f"[SCREENSHOT] Сохранен: {filename}")
            
            # Краткое уведомление
            self.control_panel.update_status(f"📸 Скриншот сохранен!", '#3498db')
            self.root.after(2000, lambda: self.control_panel.update_status("✅ Готов к работе", '#2ecc71'))
    
    def toggle_timelapse(self):
        """Переключить таймлапс"""
        if not self.is_timelapse:
            self.start_timelapse()
        else:
            self.stop_timelapse()
    
    def start_timelapse(self):
        """Начать таймлапс"""
        if self.is_paused:
            messagebox.showwarning("Пауза", "Сначала снимите с паузы!")
            return
        
        self.is_timelapse = True
        self.timelapse_start = datetime.now()
        self.timelapse_count = 0
        
        # Запускаем поток таймлапса
        self.timelapse_thread = threading.Thread(target=self.timelapse_worker, daemon=True)
        self.timelapse_thread.start()
        
        self.control_panel.update_status("🔴 Таймлапс активен", '#9b59b6')
        self.control_panel.update_timelapse_button(True)
        
        print(f"[TIMELAPSE] Таймлапс начат (интервал: {self.settings['timelapse_interval']} сек)")
    
    def stop_timelapse(self):
        """Остановить таймлапс"""
        self.is_timelapse = False
        
        if self.timelapse_start:
            duration = datetime.now() - self.timelapse_start
            hours, remainder = divmod(duration.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            
            self.control_panel.update_status(
                f"✅ Таймлапс сохранен ({self.timelapse_count} кадров)", 
                '#2ecc71'
            )
            
            print(f"[TIMELAPSE] Остановлен. Кадров: {self.timelapse_count}, "
                  f"Длительность: {hours:02d}:{minutes:02d}:{seconds:02d}")
        
        self.control_panel.update_timelapse_button(False)
    
    def timelapse_worker(self):
        """Рабочий поток для таймлапса"""
        last_capture = 0
        
        while self.is_timelapse and not self.is_paused:
            current_time = time.time()
            
            if current_time - last_capture >= self.settings['timelapse_interval']:
                # Делаем скриншот для таймлапса
                ret, frame = self.cap.read()
                if ret:
                    frame = cv2.flip(frame, 1)
                    
                    if self.settings['add_timestamp']:
                        frame = self.add_timestamp_to_frame(frame)
                    
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
                    filename = f"timelapse_{timestamp}.{self.settings['image_format']}"
                    filepath = os.path.join(self.settings['screenshots_dir'], filename)
                    
                    if self.settings['image_format'] == 'jpg':
                        cv2.imwrite(filepath, frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
                    elif self.settings['image_format'] == 'png':
                        cv2.imwrite(filepath, frame, [cv2.IMWRITE_PNG_COMPRESSION, 3])
                    else:
                        cv2.imwrite(filepath, frame)
                    
                    self.timelapse_count += 1
                    
                    # Обновляем GUI из основного потока
                    self.root.after(0, lambda: self.control_panel.update_counters(
                        video_frames=self.frame_count,
                        screenshots=self.screenshot_count,
                        timelapse=self.timelapse_count
                    ))
                    
                    print(f"[TIMELAPSE] Кадр {self.timelapse_count} сохранен")
                
                last_capture = current_time
            
            time.sleep(0.1)
    
    def toggle_pause(self):
        """Переключить паузу"""
        self.is_paused = not self.is_paused
        
        if self.is_paused:
            self.control_panel.update_status("⏸️ Пауза", '#f39c12')
            self.control_panel.update_pause_button(True)
        else:
            self.control_panel.update_status("✅ Возобновлено", '#2ecc71')
            self.control_panel.update_pause_button(False)
    
    def open_settings(self):
        """Открыть окно настроек"""
        settings_window = SettingsWindow(self.root)
        # Ждем закрытия окна настроек
        self.root.wait_window(settings_window.window)
        
        # Перезагружаем настройки
        self.settings = self.load_settings()
        print("[SETTINGS] Настройки обновлены")
    
    def open_folder(self):
        """Открыть папку с записями"""
        try:
            os.startfile(self.settings['recording_dir'])
        except:
            messagebox.showinfo("Папка", f"Записи сохраняются в:\n{self.settings['recording_dir']}")
    
    def exit_app(self):
        """Выйти из приложения"""
        if self.is_recording:
            if messagebox.askyesno("Выход", "Идет запись! Завершить запись и выйти?"):
                self.stop_recording()
            else:
                return
        
        if self.is_timelapse:
            self.stop_timelapse()
        
        if self.cap:
            self.cap.release()
        
        self.root.quit()
        self.root.destroy()

def main():
    root = tk.Tk()
    app = WebcamRecorderApp(root)
    
    # Обработка закрытия окна
    root.protocol("WM_DELETE_WINDOW", app.exit_app)
    
    root.mainloop()

if __name__ == "__main__":
    main()
