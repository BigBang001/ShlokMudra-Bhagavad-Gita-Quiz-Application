import cv2
import csv
import time
import threading
from mcq import MCQ
from utils import HandDetector, load_questions
from display import display_welcome_screen, display_question_screen, display_completion_screen
from sound import play_background_music, play_welcome_message, play_feedback

# Function to capture video
def capture_video():
    cap = cv2.VideoCapture(0)
    cap.set(3, 1280)
    cap.set(4, 720)
    return cap

def main():
    cap = capture_video()
    detector = HandDetector(detectionCon=0.8)
    background_img = cv2.imread("background.jpeg")
    background_img = cv2.resize(background_img, (1280, 720))

    pathCSV = "questions.csv"
    mcqlist = load_questions(pathCSV)

    quiz_started = False
    start_time = 0
    qNo = 0
    qTotal = len(mcqlist)
    selected_hand_id = None
    last_question_time = time.time()
    welcome_message_played = False

    music_thread = threading.Thread(target=play_background_music)
    music_thread.start()

    while True:
        success, img = cap.read()
        img = cv2.flip(img, 1)
        hands, img = detector.findHands(img, flipType=False)

        if not quiz_started:
            display_welcome_screen(img, hands, welcome_message_played)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('s'):
                quiz_started = True
                start_time = time.time()
                welcome_message_played = True
        elif qNo < qTotal:
            mcq = mcqlist[qNo]
            if time.time() - last_question_time < 1:
                display_question_screen(img, mcq, hands, selected_hand_id, detector)
                key = cv2.waitKey(1)
                continue
            img = cv2.addWeighted(img, 0.5, background_img, 0.5, 0)
            display_question_screen(img, mcq, hands, selected_hand_id, detector)
            if mcq.userAns is not None:
                play_feedback(mcq)
                qNo += 1
        else:
            display_completion_screen(img, mcqlist)
            key = cv2.waitKey(1) & 0xFF
            if key == 27:
                break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
