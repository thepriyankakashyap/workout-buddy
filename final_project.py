import cv2
import mediapipe as mp
import numpy as np
import time
from datetime import datetime
from pymongo import MongoClient

class ExerciseCounter:
    def __init__(self, weight_kg, db_name='exercise_db', collection_name='exercise_data'):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose()
        self.mp_draw = mp.solutions.drawing_utils

        self.counter = 0
        self.stage = None

        self.weight_kg = weight_kg
        self.start_time = None

        self.uri = "mongodb+srv://nkelectronicshlnp:GrKr4ht9Tn5Qkl0o@cluster0.tcdrbf5.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
        self.client = MongoClient(self.uri)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

        self.exercise_data = {'pushup': 0, 'bicep_curl': 0, 'pull_up': 0}
        self.total_calories = 0
        self.load_data()

    def load_data(self):
        today = datetime.today().strftime('%Y-%m-%d')
        record = self.collection.find_one({"date": today})

        if record:
            self.exercise_data = record.get('exercise_data', {'pushup': 0, 'bicep_curl': 0, 'pull_up': 0})
            self.total_calories = record.get('total_calories', 0)
        else:
            self.collection.insert_one({
                "date": today,
                "exercise_data": {'pushup': 0, 'bicep_curl': 0, 'pull_up': 0},
                "total_calories": 0
            })

    def save_data(self):
        today = datetime.today().strftime('%Y-%m-%d')
        self.collection.update_one(
            {"date": today},
            {"$set": {"exercise_data": self.exercise_data, "total_calories": self.total_calories}}
        )

    def calculate_angle(self, a, b, c):
        a = np.array(a)
        b = np.array(b)
        c = np.array(c)

        radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
        angle = np.abs(radians * 180.0 / np.pi)
        if angle > 180.0:
            angle = 360 - angle

        return angle

    def calculate_calories(self, exercise, duration_minutes):
        MET_values = {
            'pushup': 8,
            'bicep_curl': 3,
            'pull_up': 9
        }
        
        MET = MET_values.get(exercise, 0)
        calories_burned_per_minute = MET * self.weight_kg / 60
        return calories_burned_per_minute * duration_minutes

    def process_frame(self, image, exercise):
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.pose.process(image_rgb)

        if results.pose_landmarks:
            self.mp_draw.draw_landmarks(image, results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS)

            landmarks = results.pose_landmarks.landmark

            if exercise == 'pushup':
                shoulder = [landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                            landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
                elbow = [landmarks[self.mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                         landmarks[self.mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
                wrist = [landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                         landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST.value].y]

                angle = self.calculate_angle(shoulder, elbow, wrist)

                if angle > 90:
                    self.stage = "up"
                if angle < 60 and self.stage == 'up':
                    self.stage = "down"
                    self.counter += 1

            elif exercise == 'bicep_curl':
                shoulder = [landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                            landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
                elbow = [landmarks[self.mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                         landmarks[self.mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
                wrist = [landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                         landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST.value].y]

                angle = self.calculate_angle(shoulder, elbow, wrist)

                if angle > 160:
                    self.stage = "down"
                if angle < 30 and self.stage == 'down':
                    self.stage = "up"
                    self.counter += 1

            elif exercise == 'pull_up':
                shoulder = [landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].x,
                            landmarks[self.mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
                elbow = [landmarks[self.mp_pose.PoseLandmark.LEFT_ELBOW.value].x,
                         landmarks[self.mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
                wrist = [landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST.value].x,
                         landmarks[self.mp_pose.PoseLandmark.LEFT_WRIST.value].y]

                angle = self.calculate_angle(shoulder, elbow, wrist)

                if angle < 60:
                    self.stage = "up"
                if angle > 160 and self.stage == 'up':
                    self.stage = "down"
                    self.counter += 1

            duration_minutes = (time.time() - self.start_time) / 60
            calories_burned = self.calculate_calories(exercise, duration_minutes)

            self.total_calories += calories_burned

            cv2.putText(image, f'{exercise.capitalize()} Count: {self.counter}', (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)
            cv2.putText(image, f'Calories Burned: {calories_burned:.2f}', (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)
            # cv2.putText(image, f'Total Calories: {self.total_calories:.2f}', (10, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)

        return image

    def count_exercise(self, video_path, exercise):
        self.counter = 0
        self.stage = None
        self.start_time = time.time()

        cap = cv2.VideoCapture(video_path)

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame = self.process_frame(frame, exercise)

            cv2.imshow(f'{exercise.capitalize()} Counter', frame)
            if cv2.waitKey(10) & 0xFF == ord('q'):
                break

        self.exercise_data[exercise] += self.counter
        self.save_data()

        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    weight_kg = float(input("Enter your weight in kg: "))
    exercise_counter = ExerciseCounter(weight_kg, "MyDatabase", "Cluster0")

    while True:
        exercise = input("Enter the exercise (pushup, bicep_curl, pull_up) or 'exit' to quit: ").strip().lower()
        if exercise == 'exit':
            break
        elif exercise in ['pushup', 'bicep_curl', 'pull_up']:
            video_path = input("Enter the path to the video file: ").strip()
            exercise_counter.count_exercise(video_path, exercise)
        else:
            print("Invalid exercise. Please enter one of the following: pushup, bicep_curl, pull_up.")
