"""
Basic OpenCV-only drowsiness detection (fallback option)
Uses simple eye detection without facial landmarks
"""
import cv2
import numpy as np


class BasicOpenCVDetector:
    def __init__(self):
        # Initialize OpenCV cascade classifiers
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        self.eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
        
        # Thresholds and counters
        self.closed_eye_threshold = 0.1  # Ratio of eye height to face height
        self.consecutive_frames = 3
        self.eye_counter = 0
        self.yawn_counter = 0
        
        # Previous measurements for comparison
        self.prev_eye_ratio = 0.3
        
    def detect_drowsiness(self, frame):
        """
        Basic drowsiness detection using OpenCV only
        Returns: (is_drowsy, is_yawning, frame_with_annotations)
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect faces
        faces = self.face_cascade.detectMultiScale(gray, 1.3, 5)
        
        is_drowsy = False
        is_yawning = False
        
        for (x, y, w, h) in faces:
            # Draw face rectangle
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
            
            # Region of interest for eyes (upper half of face)
            roi_gray = gray[y:y+h//2, x:x+w]
            roi_color = frame[y:y+h//2, x:x+w]
            
            # Detect eyes in face region
            eyes = self.eye_cascade.detectMultiScale(roi_gray)
            
            # Calculate eye ratio (height relative to face)
            eye_ratio = self.calculate_eye_ratio(eyes, w, h)
            
            # Check for drowsiness based on eye ratio
            if len(eyes) < 2 or eye_ratio < self.closed_eye_threshold:
                self.eye_counter += 1
                if self.eye_counter >= self.consecutive_frames:
                    is_drowsy = True
            else:
                self.eye_counter = 0
            
            # Draw eyes
            for (ex, ey, ew, eh) in eyes:
                cv2.rectangle(roi_color, (ex, ey), (ex+ew, ey+eh), (0, 255, 0), 2)
            
            # Basic yawn detection (larger mouth area detection)
            # Region of interest for mouth (lower half of face)
            mouth_roi = gray[y+h//2:y+h, x:x+w]
            
            # Simple mouth detection using contours
            is_yawning = self.detect_yawn_basic(mouth_roi, w, h)
            
            # Draw status
            status_text = "ALERT"
            color = (0, 255, 0)
            
            if is_drowsy:
                status_text = "DROWSY DETECTED!"
                color = (0, 0, 255)
            elif is_yawning:
                status_text = "YAWNING DETECTED!"
                color = (0, 165, 255)
                
            cv2.putText(frame, status_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            cv2.putText(frame, f"Eyes: {len(eyes)}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            cv2.putText(frame, f"Eye Ratio: {eye_ratio:.3f}", (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        return is_drowsy, is_yawning, frame
    
    def calculate_eye_ratio(self, eyes, face_width, face_height):
        """Calculate eye ratio relative to face size"""
        if len(eyes) == 0:
            return 0.0
            
        total_eye_area = 0
        for (ex, ey, ew, eh) in eyes:
            total_eye_area += ew * eh
            
        face_area = face_width * face_height
        return total_eye_area / face_area if face_area > 0 else 0.0
    
    def detect_yawn_basic(self, mouth_roi, face_width, face_height):
        """Basic yawn detection using contour analysis"""
        try:
            # Apply threshold to get binary image
            _, thresh = cv2.threshold(mouth_roi, 60, 255, cv2.THRESH_BINARY_INV)
            
            # Find contours
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Find largest contour (potentially mouth)
            if contours:
                largest_contour = max(contours, key=cv2.contourArea)
                area = cv2.contourArea(largest_contour)
                
                # Get bounding box
                x, y, w, h = cv2.boundingRect(largest_contour)
                
                # Calculate aspect ratio (height/width)
                aspect_ratio = h / w if w > 0 else 0
                
                # Yawn detection criteria
                min_area = (face_width * face_height) * 0.02  # 2% of face area
                min_aspect_ratio = 0.5  # Height should be at least 50% of width
                
                return area > min_area and aspect_ratio > min_aspect_ratio
                
        except Exception as e:
            print(f"Error in yawn detection: {e}")
            return False
            
        return False


# Factory function
def create_detector():
    """Factory function to create detector instance"""
    try:
        return BasicOpenCVDetector()
    except Exception as e:
        print(f"Error creating basic OpenCV detector: {e}")
        return None