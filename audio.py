import pygame

def play(file):
    pygame.mixer.init()
    pygame.mixer.music.load("audio/" + file + ".ogg")
    pygame.mixer.music.set_volume(1)
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy() == True:
        continue