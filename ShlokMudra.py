import cv2
import csv
from cvzone.HandTrackingModule import HandDetector
import cvzone
import time
import threading
import pygame
import pyttsx3
import numpy as np

pygame.mixer.init()

# Function to display text on the image
def display_text(img, text, position, size, color, thickness):
    cv2.putText(img, text, position, cv2.FONT_HERSHEY_SIMPLEX, size, color, thickness, cv2.LINE_AA)

cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)
detector = HandDetector(detectionCon=0.8)

background_path = "background.jpeg"
background_img = cv2.imread(background_path)

if background_img is None:
    print(f"Error: Unable to load the background image from {background_path}")
    exit()

background_img = cv2.resize(background_img, (1280, 720))  # Resize the background image to match webcam feed size

hand_reset_timeout = 2
quiz_started = False
start_time = 0
countdown_time = 4
question_delay = 1

correct_sound = pygame.mixer.Sound('correct.mp3')
incorrect_sound = pygame.mixer.Sound('incorrect.mp3')
background_music = "background_music.mp3"

class MCQ():
    def __init__(self, data):
        self.question = data[0]
        self.option1 = data[1]
        self.option2 = data[2]
        self.option3 = data[3]
        self.option4 = data[4]
        self.Answer = int(data[5])
        self.userAns = None
        self.cursor_history = []
        self.selected_hand_id = None

    def update(self, cursor, bboxs, selected_hand_id):
        if selected_hand_id is not None and self.selected_hand_id is not None:
            if selected_hand_id != self.selected_hand_id:
                return

        self.cursor_history.append(cursor)
        if len(self.cursor_history) > 5:
            self.cursor_history.pop(0)

        avg_cursor = (
            sum(coord[0] for coord in self.cursor_history) / len(self.cursor_history),
            sum(coord[1] for coord in self.cursor_history) / len(self.cursor_history),
        )

        for x, bbox in enumerate(bboxs):
            x1, y1, x2, y2 = bbox
            if x1 < avg_cursor[0] < x2 and y1 < avg_cursor[1] < y2:
                self.userAns = x + 1

pathCSV = "questions.csv"
with open(pathCSV, newline="\n", encoding='latin-1') as f:
    reader = csv.reader(f)
    dataAll = list(reader)[1:]

mcqlist = [MCQ(q) for q in dataAll]

print("Total MCQ Objects Created:", len(mcqlist))

qNo = 0
qTotal = len(dataAll)
selected_hand_id = None
last_question_time = time.time()
welcome_message_played = False  # Flag to track if the welcome message has been played

def play_background_music():
    pygame.mixer.music.load(background_music)
    pygame.mixer.music.play(-1)

music_thread = threading.Thread(target=play_background_music)
music_thread.start()

while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)
    hands, img = detector.findHands(img, flipType=False)

    if not quiz_started:
        if hands and not welcome_message_played:
            engine = pyttsx3.init()
            engine.setProperty('volume', 0.9)
            rate = engine.getProperty('rate')
            engine.setProperty('rate', rate - 60)
            
            # Select Indian English female voice
            voices = engine.getProperty('voices')
            indian_english_female_voice = voices[1].id
            engine.setProperty('voice', indian_english_female_voice)
            
            engine.say("Namaste! Welcome to the Bhagavad Gita Quiz.")
            engine.runAndWait()
            welcome_message_played = True

        display_mess = "WELCOME TO THE SHRIMAD BHAGVAT GITA QUIZ"
        start_option_text = "Press 'S' to Start Quiz"

        # Use a colorful combination for the text
        display_color = (255, 165, 0)  # Orange
        start_option_color = (0, 255, 255)  # Cyan

        cv2.putText(img, display_mess, (100, 300), cv2.FONT_HERSHEY_SIMPLEX, 1.5, display_color, 3, cv2.LINE_AA)
        cv2.putText(img, start_option_text, (350, 200), cv2.FONT_HERSHEY_SIMPLEX, 1.3, start_option_color, 3,
                    cv2.LINE_AA)

        cv2.imshow("Img", img)
        key = cv2.waitKey(1) & 0xFF

        if key == ord('s'):
            quiz_started = True
            start_time = time.time()

    elif qNo < qTotal:
        mcq = mcqlist[qNo]

        if time.time() - last_question_time < question_delay:
            question_text = f"Question {qNo + 1}: {mcq.question}"
            cv2.putText(img, question_text, (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
            cv2.imshow("Img", img)
            cv2.waitKey(1)
            continue

        img = cv2.addWeighted(img, 0.5, background_img, 0.5, 0)

        cv2.putText(img, mcq.question, (150, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 3, cv2.LINE_AA)
        cv2.putText(img, f"a) {mcq.option1}", (150, 250), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 3, cv2.LINE_AA)
        cv2.putText(img, f"b) {mcq.option2}", (550, 250), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 3, cv2.LINE_AA)
        cv2.putText(img, f"c) {mcq.option3}", (150, 400), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 3, cv2.LINE_AA)
        cv2.putText(img, f"d) {mcq.option4}", (550, 400), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 3, cv2.LINE_AA)

        if hands:
            for hand in hands:
                lmList = hand["lmList"]
                cursor = lmList[8]
                length, _ = detector.findDistance(lmList[8], lmList[12])

                if length < 68:
                    selected_hand_id = hand.get("id", None)
                    mcq.update(cursor, [(150, 250, 550, 400), (550, 250, 950, 400), (150, 400, 550, 550),
                                        (550, 400, 950, 550)], selected_hand_id)
                    print(mcq.userAns)
                    if mcq.userAns is not None:
                        correct_answer = mcq.Answer
                        user_answer = mcq.userAns
                        if correct_answer == user_answer:
                            correct_sound.play()
                            engine_correct = pyttsx3.init()
                            engine_correct.say("Correct!")
                            engine_correct.runAndWait()
                            feedback_text = "Correct!"
                            feedback_color = (0, 255, 0)
                        else:
                            incorrect_sound.play()
                            engine_incorrect = pyttsx3.init()
                            engine_incorrect.say("Incorrect!")
                            engine_incorrect.runAndWait()
                            feedback_text = "Incorrect!"
                            feedback_color = (0, 0, 255)

                        cv2.putText(img, feedback_text, (950, 350), cv2.FONT_HERSHEY_SIMPLEX, 1.5, feedback_color, 3, cv2.LINE_AA)
                        cv2.imshow("Img", img)
                        time.sleep(3)

                        qNo += 1

        # Change this line for 10 questions
        barVal = 150 + (950 // qTotal) * qNo
        cv2.rectangle(img, (150, 600), (barVal, 650), (0, 255, 0), cv2.FILLED)
        cv2.rectangle(img, (150, 600), (1100, 650), (255, 255, 255), 5)
        img, _ = cvzone.putTextRect(img, f'{round((qNo / qTotal) * 100)}%', [1130, 635], 2, 2, offset=16)

    else:
        score = 0
        for mcq in mcqlist:
            if mcq.Answer == mcq.userAns:
                score += 1
        score = round((score / 10) * 100)  # Updated formula for score calculation
        completion_text = "Quiz Completed! Your Score:"
        score_text = f'{score}%'
        cv2.putText(img, completion_text, (300, 250), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 4, cv2.LINE_AA)
        cv2.putText(img, score_text, (500, 350), cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 255, 0), 5, cv2.LINE_AA)

        # Calculate the starting position for the bottom box to be centered at the bottom
        box_height = 100
        box_width = 100
        start_x = (img.shape[1] - box_width) // 2
        start_y = img.shape[0] - box_height

        bottom_box = np.zeros((box_height, img.shape[1], 3), dtype=np.uint8)
        img[start_y:, :, :] = bottom_box

        image_to_paste = cv2.imread("qr.png")
        image_to_paste = cv2.resize(image_to_paste, (box_width, box_height))
    
        # Paste the image at the calculated position
        img[start_y:start_y + box_height, start_x:start_x + box_width, :] = image_to_paste

        # Display "Scan this surprise" text just above the QR code
        surprise_text = "Scan this surprise"
        surprise_position = ((img.shape[1] - cv2.getTextSize(surprise_text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)[0][0]) // 2, start_y - 10)
        display_text(img, surprise_text, surprise_position, 0.7, (255, 0, 0), 2)

        # Display correct answers
        correct_answers_text = "Correct Answers:"
        display_text(img, correct_answers_text, (50, 50), 1.5, (255, 255, 255), 3)

        # Display correct answers for each question
        for i, mcq in enumerate(mcqlist):
         correct_answer_text = f"Q{i + 1}: {mcq.Answer}) {mcq.option1 if mcq.Answer == 1 else mcq.option2 if mcq.Answer == 2 else mcq.option3 if mcq.Answer == 3 else mcq.option4}"
         display_text(img, correct_answer_text, (50, 90 + i * 30), 0.5, (255, 255, 255), 1)


    cv2.imshow("Img", img)
    key = cv2.waitKey(1) & 0xFF

    if key == 27:
        pygame.mixer.music.stop()
        break

cap.release()
cv2.destroyAllWindows()
