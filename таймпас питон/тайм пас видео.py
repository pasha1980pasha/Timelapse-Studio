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
            print(f"Created recording folder: {RECORDING_DIR}")
        
        # Инициализируем камеру
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            raise SystemExit("Error: Cannot connect to webcam")
        
        # Устанавливаем параметры камеры
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_RESOLUTION[0])
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_RESOLUTION[1])
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        
        # Получаем реальные параметры
        self.frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        self.fps = int(self.cap.get(cv2.CAP_PROP_FPS))
        
        print(f"Webcam initialized")
        print(f"Resolution: {self.frame_width}x{self.frame_height}")
        print(f"FPS: {self.fps}")
        print(f"\nControls:")
        print(f"  R - Start/Stop recording")
        print(f"  Q - Exit program")
        print(f"\nRecordings saved to: {RECORDING_DIR}")
    
    def start_recording(self):
        """Start video recording"""
        if self.is_recording:
            return False
            
        # Generate unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.video_filename = os.path.join(RECORDING_DIR, f"webcam_{timestamp}.avi")
        
        # Create VideoWriter
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        self.video_writer = cv2.VideoWriter(
            self.video_filename,
            fourcc,
            RECORDING_FPS,
            (self.frame_width, self.frame_height)
        )
        
        if not self.video_writer.isOpened():
            print("Error: Cannot create video file")
            return False
        
        self.is_recording = True
        self.recording_start_time = datetime.now()
        self.frame_count = 0
        print(f"\n[RECORDING] Started: {self.video_filename}")
        return True
    
    def stop_recording(self):
        """Stop video recording"""
        if self.is_recording and self.video_writer is not None:
            self.video_writer.release()
            self.video_writer = None
            self.is_recording = False
            
            if self.recording_start_time:
                duration = (datetime.now() - self.recording_start_time).total_seconds()
                print(f"[RECORDING] Stopped. Duration: {duration:.1f} sec, Frames: {self.frame_count}")
                print(f"[RECORDING] File saved: {self.video_filename}")
            
            self.recording_start_time = None
            return True
        return False
    
    def write_frame(self, frame):
        """Write frame to video"""
        if self.is_recording and self.video_writer is not None:
            self.video_writer.write(frame)
            self.frame_count += 1
    
    def add_timestamp(self, frame):
        """Add timestamp to frame"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Main timestamp (top left corner)
        cv2.putText(frame, f"{current_time}", 
                   (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 
                   TIMESTAMP_FONT_SCALE, 
                   TIMESTAMP_COLOR, 2)
        
        # If recording, add recording indicator
        if self.is_recording:
            # Red recording circle
            cv2.circle(frame, (self.frame_width - 40, 30), 10, (0, 0, 255), -1)
            cv2.putText(frame, "REC", 
                       (self.frame_width - 90, 35), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
            
            # Recording duration
            if self.recording_start_time:
                elapsed = (datetime.now() - self.recording_start_time).total_seconds()
                time_str = time.strftime('%H:%M:%S', time.gmtime(elapsed))
                cv2.putText(frame, f"[{time_str}]", 
                           (self.frame_width - 200, 35), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
    
    def add_status_info(self, frame):
        """Add status information"""
        status_y = 60
        
        # Recording status
        if self.is_recording:
            status_text = "STATUS: RECORDING"
            status_color = (0, 0, 255)  # Red
            if self.frame_count > 0:
                status_text += f" ({self.frame_count} frames)"
        else:
            status_text = "STATUS: READY"
            status_color = (0, 255, 0)  # Green
        
        cv2.putText(frame, status_text, 
                   (10, status_y), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, status_color, 2)
        
        # Control instructions (English only)
        cv2.putText(frame, "R - Start/Stop, Q - Quit", 
                   (10, self.frame_height - 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    def process_frame(self):
        """Process one frame from camera"""
        ret, frame = self.cap.read()
        if not ret:
            print("Error: Cannot get frame from camera")
            return None
        
        # Mirror flip (like normal webcam)
        frame = cv2.flip(frame, 1)
        
        # Add timestamp
        self.add_timestamp(frame)
        
        # Add status information
        self.add_status_info(frame)
        
        # If recording, save the frame
        if self.is_recording:
            # For recording, use original frame (without status overlay)
            ret, clean_frame = self.cap.read()
            if ret:
                clean_frame = cv2.flip(clean_frame, 1)
                # Add only timestamp to recorded frame
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cv2.putText(clean_frame, f"{current_time}", 
                           (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 
                           TIMESTAMP_FONT_SCALE, 
                           TIMESTAMP_COLOR, 2)
                self.write_frame(clean_frame)
        
        return frame
    
    def release(self):
        """Release resources"""
        self.stop_recording()
        if self.cap.isOpened():
            self.cap.release()
        cv2.destroyAllWindows()
        print("\nResources released")

def main():
    print("\n" + "="*50)
    print("WEBCAM RECORDER WITH DISK SAVING")
    print("="*50)
    
    try:
        recorder = WebcamRecorder()
        
        print("\nStarting webcam...")
        
        while True:
            frame = recorder.process_frame()
            if frame is None:
                break
            
            # Show frame
            cv2.imshow('Webcam Recorder - Press R to record', frame)
            
            # Process key presses
            key = cv2.waitKey(1) & 0xFF
            
            if key == ord('q') or key == 27:  # Q or ESC
                print("\nExiting by user request...")
                break
            elif key == RECORD_BUTTON_KEY:  # R
                if recorder.is_recording:
                    recorder.stop_recording()
                else:
                    recorder.start_recording()
    
    except KeyboardInterrupt:
        print("\n\nProgram interrupted by user")
    except Exception as e:
        print(f"\nError: {e}")
    finally:
        if 'recorder' in locals():
            recorder.release()
        print("\nProgram finished")
        print("="*50)

if __name__ == "__main__":
    main()
