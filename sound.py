import pygame
import pyttsx3

pygame.mixer.init()

correct_sound = pygame.mixer.Sound('correct.mp3')
incorrect_sound = pygame.mixer.Sound('incorrect.mp3')
background_music = "background_music.mp3"

def play_background_music():
    pygame.mixer.music.load(background_music)
    pygame.mixer.music.play(-1)

def play_welcome_message():
    engine = pyttsx3.init()
    engine.setProperty('volume', 0.9)
    rate = engine.getProperty('rate')
    engine.setProperty('rate', rate - 60)
    voices = engine.getProperty('voices')
    indian_english_female_voice = voices[1].id
    engine.setProperty('voice', indian_english_female_voice)
    engine.say("Namaste! Welcome to the Bhagavad Gita Quiz.")
    engine.runAndWait()

def play_feedback(mcq):
    if mcq.Answer == mcq.userAns:
        correct_sound.play()
        engine = pyttsx3.init()
        engine.say("Correct!")
        engine.runAndWait()
    else:
        incorrect_sound.play()
        engine = pyttsx3.init()
        engine.say("Incorrect!")
        engine.runAndWait()
