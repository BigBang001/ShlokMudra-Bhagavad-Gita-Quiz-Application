import csv
from cvzone.HandTrackingModule import HandDetector

from mcq import MCQ

def load_questions(pathCSV):
    with open(pathCSV, newline="\n", encoding='latin-1') as f:
        reader = csv.reader(f)
        dataAll = list(reader)[1:]
    return [MCQ(q) for q in dataAll]

def HandDetector(detectionCon=0.8):
    return HandDetector(detectionCon)
