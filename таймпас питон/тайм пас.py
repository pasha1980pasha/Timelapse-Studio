import cv2
import os
import numpy as np
from datetime import datetime
import time

# Настройки записи
CAMERA_RESOLUTION = (1280, 720)
RECORDING_FPS = 20
RECORDING_DIR = "webcam_recordings"
RECORD_BUTTON_KEY = ord('r')  # Клавиша R для старта/стопа записи
TIMESTAMP_FONT_SCALE = 0.6
TIMESTAMP_COLOR = (0, 255, 0)  # Зеленый цвет

class WebcamRecorder:
    def __init__(self):
        self.is_recording = False
        self.video_writer = None
        self.start_time = None
        self.video_filename = None
        self.frame_count = 0
        self.recording_start_time = None
        
        # Создаем папку для записей
        if not os.path.exists(RECORDING_DIR):
            os.makedirs(RECORDING_DIR)
            print(f"Создана папка для записей: {RECORDING_DIR}")
        
        # Инициализируем камеру
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            raise SystemExit("Ошибка: Не удалось подключиться к веб-камере")
        
        # Устанавливаем параметры камеры
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_RESOLUTION[0])
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_RESOLUTION[1])
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        
        # Получаем реальные параметры
        self.frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.fps = int(self.cap.get(cv2.CAP_PROP_FPS))
        
        print(f"Веб-камера инициализирована")
        print(f"Разрешение: {self.frame_width}x{self.frame_height}")
        print(f"FPS: {self.fps}")
        print(f"\nУправление:")
        print(f"  R - Начать/остановить запись")
        print(f"  Q - Выйти из программы")
        print(f"\nЗаписи сохраняются в папке: {RECORDING_DIR}")
    
    def start_recording(self):
        """Начать запись видео"""
        if self.is_recording:
            return False
            
        # Генерируем уникальное имя файла
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.video_filename = os.path.join(RECORDING_DIR, f"webcam_{timestamp}.avi")
        
        # Создаем VideoWriter
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        self.video_writer = cv2.VideoWriter(
            self.video_filename,
            fourcc,
            RECORDING_FPS,
            (self.frame_width, self.frame_height)
        )
        
        if not self.video_writer.isOpened():
            print("Ошибка: Не удалось создать файл для записи")
            return False
        
        self.is_recording = True
        self.recording_start_time = datetime.now()
        self.frame_count = 0
        print(f"\n[ЗАПИСЬ] Начата запись в файл: {self.video_filename}")
        return True
    
    def stop_recording(self):
        """Остановить запись видео"""
        if self.is_recording and self.video_writer is not None:
            self.video_writer.release()
            self.video_writer = None
            self.is_recording = False
            
            if self.recording_start_time:
                duration = (datetime.now() - self.recording_start_time).total_seconds()
                print(f"[ЗАПИСЬ] Остановлена. Длительность: {duration:.1f} сек, Кадров: {self.frame_count}")
                print(f"[ЗАПИСЬ] Файл сохранен: {self.video_filename}")
            
            self.recording_start_time = None
            return True
        return False
    
    def write_frame(self, frame):
        """Записать кадр в видео"""
        if self.is_recording and self.video_writer is not None:
            self.video_writer.write(frame)
            self.frame_count += 1
    
    def add_timestamp(self, frame):
        """Добавить временную метку на кадр"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Основная временная метка (верхний левый угол)
        cv2.putText(frame, f"{current_time}", 
                   (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 
                   TIMESTAMP_FONT_SCALE, 
                   TIMESTAMP_COLOR, 2)
        
        # Если идет запись, добавляем дополнительную информацию
        if self.is_recording:
            # Индикатор записи (красный круг)
            cv2.circle(frame, (self.frame_width - 40, 30), 10, (0, 0, 255), -1)
            cv2.putText(frame, "REC", 
                       (self.frame_width - 90, 35), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            
            # Продолжительность записи
            if self.recording_start_time:
                elapsed = (datetime.now() - self.recording_start_time).total_seconds()
                time_str = time.strftime('%H:%M:%S', time.gmtime(elapsed))
                cv2.putText(frame, f"[{time_str}]", 
                           (self.frame_width - 200, 35), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
    
    def add_status_info(self, frame):
        """Добавить информацию о статусе"""
        status_y = 60
        
        # Статус записи
        if self.is_recording:
            status_text = "СТАТУС: ЗАПИСЬ ИДЕТ"
            status_color = (0, 0, 255)  # Красный
            if self.frame_count > 0:
                status_text += f" ({self.frame_count} кадров)"
        else:
            status_text = "СТАТУС: ОЖИДАНИЕ"
            status_color = (0, 255, 0)  # Зеленый
        
        cv2.putText(frame, status_text, 
                   (10, status_y), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, status_color, 2)
        
        # Инструкции
        cv2.putText(frame, "R - запись/стоп, Q - выход", 
                   (10, self.frame_height - 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    def process_frame(self):
        """Обработать один кадр с камеры"""
        ret, frame = self.cap.read()
        if not ret:
            print("Ошибка: Не удалось получить кадр с камеры")
            return None
        
        # Зеркальное отражение (как в обычной веб-камере)
        frame = cv2.flip(frame, 1)
        
        # Добавляем временную метку
        self.add_timestamp(frame)
        
        # Добавляем информацию о статусе
        self.add_status_info(frame)
        
        # Если идет запись, сохраняем кадр
        if self.is_recording:
            # Для записи используем оригинальный кадр (без статусной информации)
            ret, clean_frame = self.cap.read()
            if ret:
                clean_frame = cv2.flip(clean_frame, 1)
                # Добавляем только временную метку на записываемый кадр
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cv2.putText(clean_frame, f"{current_time}", 
                           (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 
                           TIMESTAMP_FONT_SCALE, 
                           TIMESTAMP_COLOR, 2)
                self.write_frame(clean_frame)
        
        return frame
    
    def release(self):
        """Освободить ресурсы"""
        self.stop_recording()
        if self.cap.isOpened():
            self.cap.release()
        cv2.destroyAllWindows()
        print("\nРесурсы освобождены")

def main():
    print("\n" + "="*50)
    print("ВЕБ-КАМЕРА С ЗАПИСЬЮ НА ДИСК")
    print("="*50)
    
    try:
        recorder = WebcamRecorder()
        
        print("\nЗапуск веб-камеры...")
        
        while True:
            frame = recorder.process_frame()
            if frame is None:
                break
            
            # Показываем кадр
            cv2.imshow('Webcam Recorder - Нажмите R для записи', frame)
            
            # Обработка нажатий клавиш
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q') or key == 27:  # Q или ESC
                print("\nЗавершение работы по запросу пользователя...")
                break
            elif key == RECORD_BUTTON_KEY:  # R
                if recorder.is_recording:
                    recorder.stop_recording()
                else:
                    recorder.start_recording()
    
    except KeyboardInterrupt:
        print("\n\nРабота прервана пользователем")
    except Exception as e:
        print(f"\nОшибка: {e}")
    finally:
        if 'recorder' in locals():
            recorder.release()
        print("\nПрограмма завершена")
        print("="*50)

if __name__ == "__main__":
    main()
