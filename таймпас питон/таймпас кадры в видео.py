import cv2
import os
import time
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import threading
from PIL import Image, ImageTk

class SimpleTimelapse:
    """Простой таймлапс с созданием видео"""
    def __init__(self, root):
        self.root = root
        self.root.title("Простой таймлапс")
        self.root.geometry("550x500")
        
        # Настройки
        self.interval = 300
        self.is_running = False
        self.frame_count = 0
        self.cap = None
        self.thread = None
        
        # Для видео
        self.fps = 24
        
        # Создаем GUI
        self.create_gui()
        
        # Инициализируем камеру
        self.init_camera()
        
        # Обновляем видео
        self.update_video()
    
    def create_gui(self):
        # Заголовок
        tk.Label(self.root, text="🎥 Простой таймлапс", 
                font=("Arial", 16, "bold")).pack(pady=10)
        
        # Описание
        tk.Label(self.root, text="Делает 1 кадр через заданный интервал",
                font=("Arial", 10)).pack()
        
        # Интервал
        interval_frame = tk.Frame(self.root)
        interval_frame.pack(pady=10)
        
        tk.Label(interval_frame, text="Интервал:", font=("Arial", 12)).pack(side="left", padx=5)
        
        self.interval_var = tk.StringVar(value="5 минут")
        
        intervals = [
            ("1 секунда", 1),
            ("5 секунд", 5),
            ("10 секунд", 10),
            ("30 секунд", 30),
            ("1 минута", 60),
            ("5 минут", 300),
            ("10 минут", 600),
            ("30 минут", 1800),
            ("1 час", 3600),
        ]
        
        interval_combo = ttk.Combobox(interval_frame, textvariable=self.interval_var, 
                                     values=[name for name, _ in intervals], width=15, state="readonly")
        interval_combo.pack(side="left", padx=5)
        
        self.interval_map = {name: seconds for name, seconds in intervals}
        
        # Кнопка запуска/останова
        self.control_btn = tk.Button(self.root, text="▶️ Запустить таймлапс", 
                                    command=self.toggle_timelapse,
                                    font=("Arial", 12), bg='#4CAF50', fg='white',
                                    width=20, height=2)
        self.control_btn.pack(pady=10)
        
        # Статус
        self.status_label = tk.Label(self.root, text="Таймлапс выключен", 
                                    font=("Arial", 10))
        self.status_label.pack(pady=5)
        
        # Счетчик кадров
        self.counter_label = tk.Label(self.root, text="Сделано кадров: 0", 
                                     font=("Arial", 10))
        self.counter_label.pack(pady=5)
        
        # Следующий снимок
        self.next_label = tk.Label(self.root, text="", font=("Arial", 9))
        self.next_label.pack(pady=5)
        
        # Видео с камеры
        self.video_label = tk.Label(self.root, bg='black', width=320, height=240)
        self.video_label.pack(pady=10)
        
        # Время последнего снимка
        self.last_shot_label = tk.Label(self.root, text="", font=("Arial", 9))
        self.last_shot_label.pack()
        
        # Фрейм для кнопок видео
        video_buttons_frame = tk.Frame(self.root)
        video_buttons_frame.pack(pady=10)
        
        # Кнопка создания видео
        self.create_video_btn = tk.Button(video_buttons_frame, text="🎬 Создать видео", 
                                         command=self.create_video,
                                         font=("Arial", 10), bg='#2196F3', fg='white',
                                         width=15)
        self.create_video_btn.pack(side="left", padx=5)
        
        # Кнопка открытия папки
        self.open_folder_btn = tk.Button(video_buttons_frame, text="📂 Открыть папку", 
                                        command=self.open_folder,
                                        font=("Arial", 10), bg='#FF9800', fg='white',
                                        width=15)
        self.open_folder_btn.pack(side="left", padx=5)
        
        # Статус создания видео
        self.video_status_label = tk.Label(self.root, text="", font=("Arial", 9))
        self.video_status_label.pack(pady=5)
        
        # Информация
        info_frame = tk.Frame(self.root)
        info_frame.pack(pady=5)
        
        tk.Label(info_frame, text=f"Кадры: timelapse/", font=("Arial", 8)).pack(side="left", padx=10)
        tk.Label(info_frame, text=f"Видео: timelapse_videos/", font=("Arial", 8)).pack(side="left", padx=10)
    
    def init_camera(self):
        """Инициализировать камеру"""
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            messagebox.showerror("Ошибка", "Не удалось подключиться к камере!")
            self.root.quit()
            return
        
        # Создаем папки
        self.create_folders()
    
    def create_folders(self):
        """Создать необходимые папки"""
        folders = ['timelapse', 'timelapse_videos']
        for folder in folders:
            if not os.path.exists(folder):
                os.makedirs(folder)
                print(f"[Система] Создана папка: {folder}")
    
    def update_video(self):
        """Обновить видео с камеры"""
        if self.cap and not self.is_running:
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.flip(frame, 1)
                frame = cv2.resize(frame, (320, 240))
                
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = Image.fromarray(rgb_frame)
                imgtk = ImageTk.PhotoImage(image=img)
                
                self.video_label.config(image=imgtk)
                self.video_label.image = imgtk
        
        self.root.after(50, self.update_video)
    
    def take_screenshot(self):
        """Сделать снимок"""
        if not self.cap:
            return
        
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.flip(frame, 1)
            
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cv2.putText(frame, timestamp, (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            filename = f"timelapse_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            filepath = os.path.join('timelapse', filename)
            cv2.imwrite(filepath, frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
            
            self.frame_count += 1
            
            self.root.after(0, self.update_after_shot)
            
            print(f"[Таймлапс] Сохранен кадр {self.frame_count}: {filename}")
    
    def update_after_shot(self):
        """Обновить GUI после снимка"""
        self.counter_label.config(text=f"Сделано кадров: {self.frame_count}")
        self.last_shot_label.config(text=f"Последний снимок: {datetime.now().strftime('%H:%M:%S')}")
    
    def create_video(self):
        """Создать видео из кадров"""
        # Проверяем папку с кадрами
        image_folder = 'timelapse'
        if not os.path.exists(image_folder):
            messagebox.showwarning("Внимание", f"Папка '{image_folder}' не существует!")
            return
        
        # Получаем список изображений
        images = [img for img in os.listdir(image_folder) if img.lower().endswith(('.jpg', '.jpeg', '.png'))]
        
        if len(images) == 0:
            messagebox.showwarning("Внимание", f"В папке '{image_folder}' нет изображений!")
            return
        
        # Показываем сколько кадров найдено
        print(f"[Видео] Найдено {len(images)} кадров")
        
        # Сортируем по имени (в имени есть время)
        images.sort()
        
        # Берем первый кадр для определения размера
        first_image_path = os.path.join(image_folder, images[0])
        frame = cv2.imread(first_image_path)
        
        if frame is None:
            messagebox.showerror("Ошибка", f"Не удалось прочитать первый кадр: {first_image_path}")
            return
        
        height, width, _ = frame.shape
        print(f"[Видео] Размер кадра: {width}x{height}")
        
        # Создаем имя для видео
        video_name = f"timelapse_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
        video_path = os.path.join('timelapse_videos', video_name)
        
        # Создаем видео writer
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        video = cv2.VideoWriter(video_path, fourcc, self.fps, (width, height))
        
        if not video.isOpened():
            messagebox.showerror("Ошибка", "Не удалось создать видео файл!")
            return
        
        # Обновляем статус
        self.video_status_label.config(text=f"Создание видео из {len(images)} кадров...", fg='blue')
        self.create_video_btn.config(state="disabled")
        
        # Запускаем в отдельном потоке
        threading.Thread(target=self.create_video_thread, 
                        args=(video, video_path, images, image_folder), 
                        daemon=True).start()
    
    def create_video_thread(self, video, video_path, images, image_folder):
        """Создание видео в отдельном потоке"""
        total = len(images)
        successful = 0
        failed = 0
        
        for i, image in enumerate(images):
            img_path = os.path.join(image_folder, image)
            frame = cv2.imread(img_path)
            
            if frame is not None:
                video.write(frame)
                successful += 1
            else:
                print(f"[Видео] Ошибка чтения: {image}")
                failed += 1
            
            # Обновляем прогресс
            if i % 5 == 0 or i == total - 1:
                progress = (i + 1) / total * 100
                self.root.after(0, lambda p=progress, idx=i+1, t=total, s=successful, f=failed: 
                              self.update_video_progress(p, idx, t, s, f))
        
        video.release()
        
        # Обновляем статус
        self.root.after(0, lambda: self.video_status_label.config(
            text=f"Готово! {successful} кадров, {failed} ошибок", fg='green'))
        
        self.root.after(0, lambda: self.create_video_btn.config(state="normal"))
        
        if successful > 0:
            # Показываем сообщение
            duration = successful / self.fps
            self.root.after(0, lambda: messagebox.showinfo(
                "Видео создано!",
                f"Видео сохранено: {os.path.basename(video_path)}\n\n"
                f"Кадров: {successful} (ошибок: {failed})\n"
                f"Длительность: {duration:.1f} секунд\n"
                f"FPS: {self.fps}\n\n"
                f"Файл: {video_path}"
            ))
            
            print(f"[Видео] Создано: {video_path} ({successful} кадров, {duration:.1f} сек)")
        else:
            self.root.after(0, lambda: messagebox.showerror(
                "Ошибка",
                "Не удалось создать видео! Проверьте файлы с кадрами."
            ))
    
    def update_video_progress(self, progress, current, total, successful, failed):
        """Обновить прогресс создания видео"""
        self.video_status_label.config(
            text=f"Создание видео: {current}/{total} ({progress:.1f}%) | Успешно: {successful} | Ошибок: {failed}", 
            fg='blue')
    
    def open_folder(self):
        """Открыть папку с видео"""
        folder = 'timelapse_videos'
        if not os.path.exists(folder):
            self.create_folders()
        
        try:
            if os.name == 'nt':  # Windows
                os.startfile(folder)
            elif os.name == 'posix':  # macOS, Linux
                import subprocess
                subprocess.call(['open', folder] if sys.platform == 'darwin' else ['xdg-open', folder])
            print(f"[Система] Открыта папка: {folder}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось открыть папку: {e}")
    
    def timelapse_worker(self):
        """Рабочий поток таймлапса"""
        print(f"[Таймлапс] Запущен с интервалом: {self.interval} секунд")
        last_capture = 0
        
        while self.is_running:
            current_time = time.time()
            
            if current_time - last_capture >= self.interval:
                self.take_screenshot()
                last_capture = current_time
            
            if last_capture > 0:
                next_time = last_capture + self.interval
                remaining = next_time - current_time
                
                if remaining > 3600:
                    text = f"Следующий снимок через: {int(remaining//3600)} ч {int((remaining%3600)//60)} мин"
                elif remaining > 60:
                    text = f"Следующий снимок через: {int(remaining//60)} мин {int(remaining%60)} сек"
                else:
                    text = f"Следующий снимок через: {int(remaining)} сек"
                
                self.root.after(0, lambda t=text: self.next_label.config(text=t))
            
            time.sleep(1)
    
    def toggle_timelapse(self):
        """Переключить таймлапс"""
        if not self.is_running:
            self.start_timelapse()
        else:
            self.stop_timelapse()
    
    def start_timelapse(self):
        """Запустить таймлапс"""
        interval_name = self.interval_var.get()
        self.interval = self.interval_map.get(interval_name, 300)
        
        self.is_running = True
        self.frame_count = 0
        
        # Обновляем GUI
        self.status_label.config(text="✅ Таймлапс запущен", fg='green')
        self.control_btn.config(text="⏹️ Остановить таймлапс", bg='#f44336')
        self.counter_label.config(text="Сделано кадров: 0")
        self.last_shot_label.config(text="")
        self.video_status_label.config(text="")
        
        # Запускаем поток
        self.thread = threading.Thread(target=self.timelapse_worker, daemon=True)
        self.thread.start()
    
    def stop_timelapse(self):
        """Остановить таймлапс"""
        self.is_running = False
        
        # Обновляем GUI
        self.status_label.config(text="⏸️ Таймлапс остановлен", fg='red')
        self.control_btn.config(text="▶️ Запустить таймлапс", bg='#4CAF50')
        self.next_label.config(text="")
    
    def exit_app(self):
        """Выйти из приложения"""
        self.stop_timelapse()
        
        if self.cap:
            self.cap.release()
        
        self.root.quit()

def main():
    root = tk.Tk()
    app = SimpleTimelapse(root)
    
    root.protocol("WM_DELETE_WINDOW", app.exit_app)
    root.mainloop()

if __name__ == "__main__":
    import sys
    main()
