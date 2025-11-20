"""
Alternative drowsiness detection using MediaPipe for better Windows compatibility
Replaces dlib with MediaPipe Face Mesh for facial landmark detection
"""
import cv2
import numpy as np
import mediapipe as mp
from scipy.spatial import distance as dist


class MediaPipeDrowsinessDetector:
    def __init__(self):
        # Initialize MediaPipe Face Mesh
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.7
        )
        
        # Eye landmark indices for MediaPipe Face Mesh
        self.LEFT_EYE_LANDMARKS = [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246]
        self.RIGHT_EYE_LANDMARKS = [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398]
        
        # Mouth landmarks for yawn detection
        self.MOUTH_LANDMARKS = [13, 14, 17, 18, 269, 270, 267, 271, 272, 407, 408, 409, 415, 310, 311, 312, 13, 82, 81, 80, 78]
        
        # Thresholds
        self.EAR_THRESHOLD = 0.25
        self.MOUTH_AR_THRESHOLD = 0.7
        self.CONSECUTIVE_FRAMES = 3
        
        # Counters
        self.ear_counter = 0
        self.mouth_counter = 0
        
    def eye_aspect_ratio(self, eye_landmarks):
        """Calculate eye aspect ratio"""
        if len(eye_landmarks) < 6:
            return 0.3  # Default safe value
            
        # Vertical distances
        A = dist.euclidean(eye_landmarks[1], eye_landmarks[5])
        B = dist.euclidean(eye_landmarks[2], eye_landmarks[4])
        
        # Horizontal distance
        C = dist.euclidean(eye_landmarks[0], eye_landmarks[3])
        
        # Eye aspect ratio
        ear = (A + B) / (2.0 * C) if C > 0 else 0.3
        return ear
    
    def mouth_aspect_ratio(self, mouth_landmarks):
        """Calculate mouth aspect ratio for yawn detection"""
        if len(mouth_landmarks) < 8:
            return 0.3  # Default safe value
            
        # Vertical distances
        A = dist.euclidean(mouth_landmarks[2], mouth_landmarks[6])  # Top to bottom
        B = dist.euclidean(mouth_landmarks[3], mouth_landmarks[7])  # Top to bottom
        
        # Horizontal distance
        C = dist.euclidean(mouth_landmarks[0], mouth_landmarks[4])  # Left to right
        
        # Mouth aspect ratio
        mar = (A + B) / (2.0 * C) if C > 0 else 0.3
        return mar
    
    def get_landmarks(self, image):
        """Extract facial landmarks using MediaPipe"""
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(image_rgb)
        
        if not results.multi_face_landmarks:
            return None, None, None
            
        face_landmarks = results.multi_face_landmarks[0]
        h, w = image.shape[:2]
        
        # Extract eye landmarks
        left_eye = []
        right_eye = []
        mouth = []
        
        try:
            # Left eye landmarks
            for idx in [33, 160, 158, 133, 153, 144]:  # Simplified eye landmarks
                landmark = face_landmarks.landmark[idx]
                left_eye.append((int(landmark.x * w), int(landmark.y * h)))
            
            # Right eye landmarks  
            for idx in [362, 385, 387, 263, 373, 380]:  # Simplified eye landmarks
                landmark = face_landmarks.landmark[idx]
                right_eye.append((int(landmark.x * w), int(landmark.y * h)))
                
            # Mouth landmarks
            for idx in [13, 14, 269, 270, 17, 18, 200, 199]:  # Simplified mouth landmarks
                landmark = face_landmarks.landmark[idx]
                mouth.append((int(landmark.x * w), int(landmark.y * h)))
                
        except (IndexError, AttributeError):
            return None, None, None
            
        return left_eye, right_eye, mouth
    
    def detect_drowsiness(self, frame):
        """
        Main drowsiness detection function
        Returns: (is_drowsy, is_yawning, frame_with_annotations)
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Get facial landmarks
        left_eye, right_eye, mouth = self.get_landmarks(frame)
        
        if left_eye is None or right_eye is None:
            return False, False, frame
            
        # Calculate EAR for both eyes
        left_ear = self.eye_aspect_ratio(left_eye)
        right_ear = self.eye_aspect_ratio(right_eye)
        avg_ear = (left_ear + right_ear) / 2.0
        
        # Calculate MAR for yawn detection
        mouth_ar = 0.0
        is_yawning = False
        if mouth:
            mouth_ar = self.mouth_aspect_ratio(mouth)
            
        # Check for drowsiness
        is_drowsy = False
        if avg_ear < self.EAR_THRESHOLD:
            self.ear_counter += 1
            if self.ear_counter >= self.CONSECUTIVE_FRAMES:
                is_drowsy = True
        else:
            self.ear_counter = 0
            
        # Check for yawning
        if mouth_ar > self.MOUTH_AR_THRESHOLD:
            self.mouth_counter += 1
            if self.mouth_counter >= self.CONSECUTIVE_FRAMES:
                is_yawning = True
        else:
            self.mouth_counter = 0
            
        # Draw annotations on frame
        frame_annotated = self.draw_annotations(frame, left_eye, right_eye, mouth, 
                                              avg_ear, mouth_ar, is_drowsy, is_yawning)
        
        return is_drowsy, is_yawning, frame_annotated
    
    def draw_annotations(self, frame, left_eye, right_eye, mouth, ear, mar, is_drowsy, is_yawning):
        """Draw detection annotations on frame"""
        # Draw eye contours
        if left_eye:
            cv2.polylines(frame, [np.array(left_eye, dtype=np.int32)], True, (0, 255, 0), 1)
        if right_eye:
            cv2.polylines(frame, [np.array(right_eye, dtype=np.int32)], True, (0, 255, 0), 1)
        if mouth:
            cv2.polylines(frame, [np.array(mouth, dtype=np.int32)], True, (0, 0, 255), 1)
            
        # Status text
        status_text = "ALERT"
        color = (0, 255, 0)  # Green
        
        if is_drowsy:
            status_text = "DROWSY DETECTED!"
            color = (0, 0, 255)  # Red
        elif is_yawning:
            status_text = "YAWNING DETECTED!"
            color = (0, 165, 255)  # Orange
            
        # Draw status
        cv2.putText(frame, status_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        cv2.putText(frame, f"EAR: {ear:.3f}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.putText(frame, f"MAR: {mar:.3f}", (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        return frame


# Factory function for easy integration
def create_detector():
    """Factory function to create detector instance"""
    try:
        return MediaPipeDrowsinessDetector()
    except Exception as e:
        print(f"Error creating MediaPipe detector: {e}")
        return None