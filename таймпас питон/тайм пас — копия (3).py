import cv2
import os
import time
from datetime import datetime
import tkinter as tk
from tkinter import ttk
import threading

class SimpleTimelapse:
    """Простой таймлапс с настраиваемым интервалом"""
    def __init__(self, root):
        self.root = root
        self.root.title("Простой таймлапс")
        self.root.geometry("500x400")
        
        # Настройки
        self.interval = 300  # 5 минут по умолчанию
        self.is_running = False
        self.frame_count = 0
        self.cap = None
        self.thread = None
        
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
        interval_frame.pack(pady=20)
        
        tk.Label(interval_frame, text="Интервал:", font=("Arial", 12)).pack(side="left", padx=5)
        
        # Выбор интервала
        self.interval_var = tk.StringVar(value="5 минут")
        
        # Создаем опции
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
            ("6 часов", 21600),
            ("12 часов", 43200),
            ("1 сутки", 86400)
        ]
        
        interval_combo = ttk.Combobox(interval_frame, textvariable=self.interval_var, 
                                     values=[name for name, _ in intervals], width=15, state="readonly")
        interval_combo.pack(side="left", padx=5)
        
        # Сохраняем маппинг значений
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
        
        # Видео с камеры (маленькое)
        self.video_label = tk.Label(self.root, bg='black', width=320, height=240)
        self.video_label.pack(pady=10)
        
        # Время последнего снимка
        self.last_shot_label = tk.Label(self.root, text="", font=("Arial", 9))
        self.last_shot_label.pack()
        
        # Папка для сохранения
        tk.Label(self.root, text=f"Кадры сохраняются в: timelapse/", 
                font=("Arial", 8)).pack()
    
    def init_camera(self):
        """Инициализировать камеру"""
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            tk.messagebox.showerror("Ошибка", "Не удалось подключиться к камере!")
            self.root.quit()
            return
        
        # Создаем папку для сохранения
        if not os.path.exists('timelapse'):
            os.makedirs('timelapse')
    
    def update_video(self):
        """Обновить видео с камеры"""
        if self.cap and not self.is_running:
            ret, frame = self.cap.read()
            if ret:
                # Зеркально отражаем
                frame = cv2.flip(frame, 1)
                
                # Масштабируем для отображения
                frame = cv2.resize(frame, (320, 240))
                
                # Конвертируем для Tkinter
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Конвертируем в фотоизображение Tkinter
                from PIL import Image, ImageTk
                img = Image.fromarray(rgb_frame)
                imgtk = ImageTk.PhotoImage(image=img)
                
                # Обновляем изображение
                self.video_label.config(image=imgtk)
                self.video_label.image = imgtk
        
        # Планируем следующее обновление
        self.root.after(50, self.update_video)
    
    def take_screenshot(self):
        """Сделать снимок"""
        if not self.cap:
            return
        
        ret, frame = self.cap.read()
        if ret:
            # Зеркально отражаем
            frame = cv2.flip(frame, 1)
            
            # Добавляем время на снимок
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cv2.putText(frame, timestamp, (10, 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            
            # Сохраняем
            filename = f"timelapse_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            filepath = os.path.join('timelapse', filename)
            cv2.imwrite(filepath, frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
            
            self.frame_count += 1
            
            # Обновляем GUI в основном потоке
            self.root.after(0, self.update_after_shot)
            
            print(f"[Таймлапс] Сохранен кадр {self.frame_count}: {filename}")
    
    def update_after_shot(self):
        """Обновить GUI после снимка"""
        self.counter_label.config(text=f"Сделано кадров: {self.frame_count}")
        self.last_shot_label.config(text=f"Последний снимок: {datetime.now().strftime('%H:%M:%S')}")
    
    def timelapse_worker(self):
        """Рабочий поток таймлапса"""
        print(f"[Таймлапс] Запущен с интервалом: {self.interval} секунд")
        last_capture = 0
        
        while self.is_running:
            current_time = time.time()
            
            # Проверяем интервал
            if current_time - last_capture >= self.interval:
                self.take_screenshot()
                last_capture = current_time
            
            # Обновляем время до следующего снимка
            if last_capture > 0:
                next_time = last_capture + self.interval
                remaining = next_time - current_time
                
                # Обновляем GUI в основном потоке
                if remaining > 3600:
                    text = f"Следующий снимок через: {int(remaining//3600)} ч {int((remaining%3600)//60)} мин"
                elif remaining > 60:
                    text = f"Следующий снимок через: {int(remaining//60)} мин {int(remaining%60)} сек"
                else:
                    text = f"Следующий снимок через: {int(remaining)} сек"
                
                self.root.after(0, lambda t=text: self.next_label.config(text=t))
            
            # Небольшая пауза
            time.sleep(1)
    
    def toggle_timelapse(self):
        """Переключить таймлапс"""
        if not self.is_running:
            self.start_timelapse()
        else:
            self.stop_timelapse()
    
    def start_timelapse(self):
        """Запустить таймлапс"""
        # Получаем интервал из выбранного значения
        interval_name = self.interval_var.get()
        self.interval = self.interval_map.get(interval_name, 300)
        
        self.is_running = True
        self.frame_count = 0
        
        # Обновляем GUI
        self.status_label.config(text="✅ Таймлапс запущен", fg='green')
        self.control_btn.config(text="⏹️ Остановить таймлапс", bg='#f44336')
        self.counter_label.config(text="Сделано кадров: 0")
        self.last_shot_label.config(text="")
        
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
    main()
