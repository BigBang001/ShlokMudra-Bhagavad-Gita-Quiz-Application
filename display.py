import cv2
import numpy as np

def display_text(img, text, position, size, color, thickness):
    cv2.putText(img, text, position, cv2.FONT_HERSHEY_SIMPLEX, size, color, thickness, cv2.LINE_AA)

def display_welcome_screen(img, hands, welcome_message_played):
    display_mess = "WELCOME TO THE SHRIMAD BHAGVAT GITA QUIZ"
    start_option_text = "Press 'S' to Start Quiz"
    display_color = (255, 165, 0)
    start_option_color = (0, 255, 255)
    cv2.putText(img, display_mess, (100, 300), cv2.FONT_HERSHEY_SIMPLEX, 1.5, display_color, 3, cv2.LINE_AA)
    cv2.putText(img, start_option_text, (350, 200), cv2.FONT_HERSHEY_SIMPLEX, 1.3, start_option_color, 3, cv2.LINE_AA)
    cv2.imshow("Img", img)

def display_question_screen(img, mcq, hands, selected_hand_id, detector):
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
                mcq.update(cursor, [(150, 250, 550, 400), (550, 250, 950, 400), (150, 400, 550, 550), (550, 400, 950, 550)], selected_hand_id)
                if mcq.userAns is not None:
                    feedback_text = "Correct!" if mcq.Answer == mcq.userAns else "Incorrect!"
                    feedback_color = (0, 255, 0) if mcq.Answer == mcq.userAns else (0, 0, 255)
                    cv2.putText(img, feedback_text, (950, 350), cv2.FONT_HERSHEY_SIMPLEX, 1.5, feedback_color, 3, cv2.LINE_AA)
                    cv2.imshow("Img", img)
                    cv2.waitKey(500)

def display_completion_screen(img, mcqlist):
    score = sum([mcq.Answer == mcq.userAns for mcq in mcqlist])
    percentage = (score / len(mcqlist)) * 100
    score_text = f"QUIZ COMPLETED - Score: {score}/{len(mcqlist)} ({percentage:.2f}%)"
    completion_color = (0, 255, 0) if percentage >= 60 else (0, 0, 255)
    cv2.putText(img, score_text, (150, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, completion_color, 3, cv2.LINE_AA)
    cv2.putText(img, "Press 'ESC' to Exit", (450, 600), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 3, cv2.LINE_AA)
    cv2.imshow("Img", img)
