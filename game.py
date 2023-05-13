#!/usr/bin/env python
# -*- coding: utf-8 -*-
import random
import pygame
from pygame import mixer
import pygame, sys
from thread import  recogQ, recogQ_Get, sdStream, Get1secSpeech
import os
import shutil
import tkinter as tk
from tkinter import filedialog
import ryRecog06_TW as ry
from threading import Thread
import pygame.time as pgTime

# initialize pygame
pygame.init()

# caption and icon
pygame.display.set_caption("Catch")
icon = pygame.image.load('ele/ufo.png')
pygame.display.set_icon(icon)

# screen 
win = pygame.display.set_mode((800,600))
pygame.display.set_caption("Apple CATCHER")

# font
font = pygame.font.SysFont("dfkaisb",32)
over_font = pygame.font.Font('freesansbold.ttf', 64)

# image
background = pygame.image.load('ele/background.png')
playerImg  = pygame.image.load('ele/player_r.png')
logoImg    = pygame.image.load('menu/logo.png')
startImg   = pygame.image.load('menu/Start.png')
modeImg    = pygame.image.load('menu/Mode.png')
engImg     = pygame.image.load('menu/eng.png')
zhImg      = pygame.image.load('menu/zh.png')
taiImg  = pygame.image.load('menu/tai.png')
bulletImg  = pygame.image.load('ele/Shuriken.png')
appleImg   = pygame.image.load('ele/apple.png')

# Apples
appleX = []
appleY = []
appleX_change = []
appleY_change = []
num_of_apples = 3

for i in range(num_of_apples):
    appleX.append(random.randint(0, 736))
    appleY.append(random.randint(50, 150))
    appleX_change.append(2)
    appleY_change.append(20)

def isCollision(appleX, appleY, bulletX, bulletY):
    distance = ((appleX - bulletX) ** 2 + ((appleY - bulletY) ** 2)) ** 0.5
    if distance < 27:
        return True
    else:
        return False

def save_history(word):
    global history_str
    if len(history)==10:
        history.pop(0)
        history.append(word)
        history_str=" "
        for i in range(len(history)):
            history_str += history[i]+" "
    else:
        history.append(word)
        history_str += word +" "

def main_menu():
    while True:
        win.fill((0, 0, 0))
        win.blit(background, (0, 0))
        win.blit(logoImg, (250, 60))
        win.blit(startImg, (320,300))
        button_start = pygame.Rect(320,300,200,131)
        
        mx, my = pygame.mouse.get_pos()

        click = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    click = True

        if button_start.collidepoint((mx,my)):
            if click:
                mode_menu() 
        
        pygame.display.update()

def mode_menu():
    while True:
        win.fill((0, 0, 0))
        win.blit(background, (0, 0))
        win.blit(engImg, (150, 250))
        win.blit(zhImg, (350,250))
        win.blit(taiImg, (550, 250))
        win.blit(modeImg, (290, 100))

        button_eng    = pygame.Rect(150,250,150,150)
        button_zh     = pygame.Rect(350,250,150,150)
        button_tai = pygame.Rect(550,250,150,150)

        mx, my = pygame.mouse.get_pos()

        click = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    click = True
        
        if button_eng.collidepoint((mx,my)):
            if click:
                speech_game_loop(lan='eng')
        if button_zh.collidepoint((mx,my)):
            if click:
                speech_game_loop(lan='zh')
        if button_tai.collidepoint((mx,my)):
            if click:
                speech_game_loop(lan='tai')

        pygame.display.update()

def speech_game_loop(lan = 'eng'):

    # choose the model's language
    if lan == 'eng':
        import ryRecog06_eng as rec
    elif lan == 'zh':
        import ryRecog06_TW as rec
    elif lan == 'tai':
        import ryRecog06_tai as rec

    #inital setting
    playerX = 370
    playerY = 480
    playerX_change = 0
    playerY_change = 0
    bulletX = 0
    bulletY = 480
    bulletX_change = 0
    bulletY_change = 10
    bullet_state = "ready"
    global history
    history = ['_silence_']
    global history_str
    history_str = " "
    score_value = 0
    global Recog_run
    Recog_run = True
    pgClock = pgTime.Clock()
    fps = 30 # loop/sec 
    recProbToConfirm = 0.8

    sStream = sdStream()
    sStream.start()

    Recog_thread = Thread(target= Recog,  
                       args=(recogQ,rec), 
                       daemon= True)
    Recog_thread.start()
    
    running = True
    while running:
        pgClock.tick(fps)
        win.fill((0, 0, 0))
        win.blit(background, (0, 0))
    
        recogQ_list= recogQ_Get(recogQ) 
        recResult = ' '
        prob=0.0
        for recResult, prob in recogQ_list:
            if prob > recProbToConfirm:
                if history[-1] == recResult:
                    break
                if   recResult in ['left','左']:
                    playerX_change = -1
                    save_history(recResult)
                elif recResult in ['right','右']:
                    playerX_change = +1
                    save_history(recResult)
                elif recResult in ['forward','up','前進','上']:
                    playerY_change = -1
                    save_history(recResult)            
                elif recResult in ['backward','down','後退','下']:
                    playerY_change = +1
                    save_history(recResult)   
                elif recResult in ['yes', 'on', 'go','可以','開','去']:
                    save_history(recResult)
                    if bullet_state == "ready":
                        bullet_state = "fire"
                        bulletSound = mixer.Sound('ele/laser.wav')
                        bulletSound.play()
                        # Get the current x cordinate of the spaceship
                        bulletX = playerX
                        bulletY = playerY      
                elif recResult in ['no','off','stop','不可','關']:
                    save_history(recResult)
                    playerX_change = 0
                    playerY_change = 0
       
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # player Movement
        playerX += playerX_change
        if playerX <= 0:
            playerX = 0
        elif playerX >= 736:
            playerX = 736

        playerY += playerY_change
        if playerY <= 0:
            playerY = 0
        elif playerY >= 480:
            playerY = 480

        win.blit(playerImg, (playerX, playerY))

        # Bullet Movement
        if bulletY <= 0:
            bulletY = 480
            bullet_state = "ready"
        
        if bullet_state == "fire":
            bulletY -= 10
            win.blit(bulletImg, (bulletX , bulletY))

        # Apple Movement
        for i in range(num_of_apples):
            # Game Over
            if appleY[i] > 440:
                for j in range(num_of_apples):
                    appleY[j] = 2000

                over_text = over_font.render("GAME OVER", True, (255, 255, 255))
                win.blit(over_text, (200, 250))
                break

            appleX[i] += appleX_change[i]
            if appleX[i] <= 0:
                appleX_change[i] = 4
                appleY[i] += appleY_change[i]
            elif appleX[i] >= 736:
                appleX_change[i] = -4
                appleY[i] += appleY_change[i]

            # Collision
            collision = isCollision(appleX[i], appleY[i], bulletX, bulletY)
            if collision:
                explosionSound = mixer.Sound("ele/coin.wav")
                explosionSound.play()
                score_value += 1
                appleX[i] = random.randint(0, 736)
                appleY[i] = random.randint(50, 150)

            win.blit(appleImg, (appleX[i], appleY[i]))

        history_label = font.render(history_str ,True , (255,255,0))
        win.blit(history_label, (10, 550))
        
        score = font.render("Score : " + str(score_value), True, (255, 255, 255))
        win.blit(score, (10, 10))

        recR = font.render(recResult, True, (0, 255, 255))
        win.blit(recR, (playerX-50, playerY+50))
    
        pygame.display.update()
    

    sStream.stop()
    sStream.close()
    Recog_run = False
    Recog_thread.join()

def Recog(q,rec): 
    global Recog_run
    print('Recog start ....') 
    while Recog_run:
 
        x= Get1secSpeech()
        yp= rec.recWav(x, probOut= True)
        y=    yp[0,0]
        prob= yp[1,0].astype('float32')
    
        q.put((y,prob))
        
    print('Recog ended ....')

main_menu()
        


        