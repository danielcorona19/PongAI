import pygame
import random
import numpy as np
from pygame import *

RIGHT = 1
LEFT = 2

BLOCK_SIZE = 10
SPEED = 40
BAR_SCALE = 5

class Game:
    
    def __init__(self,w=600,h=600):
        self.w = w
        self.h = h
        self.display = pygame.display.set_mode([self.w, self.h])
        pygame.display.set_caption('Tennis')
        self.clock = pygame.time.Clock()
        self.reset()
        self.move = True
        # self.action = [1,0,0]
        
    def reset(self):
        self.direction = 0
        
        self.ballpos = [300, 400]
        self.ball = pygame.Surface((BLOCK_SIZE, BLOCK_SIZE))
        self.ball.fill((255, 255, 255))
        
        self.barpos = [300, 550]
        self.bar = pygame.Surface((BAR_SCALE*BLOCK_SIZE, BLOCK_SIZE))
        self.bar.fill((255, 255, 255))
        
        self.rx = random.randint(0,1)
        if self.rx == 0:
            self.rx = 5
        else:
            self.rx = -5
        self.ry = random.randint(-5,-3)
        
        self.score = 0
        self.frame_iteration = 0
        self.new_collision = True
        
    def step(self, action):
        self.frame_iteration += 1
        self.clock.tick(SPEED)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            # if event.type == pygame.KEYDOWN:
            #     if event.key == pygame.K_RIGHT:
            #         self.action = [0, 1, 0]
            #     if event.key == pygame.K_LEFT:
            #         self.action = [0, 0, 1]
            # if event.type == pygame.KEYUP:
            #     if event.key == pygame.K_RIGHT:
            #         self.action = [1, 0, 0]
            #     if event.key == pygame.K_LEFT:
            #         self.action = [1, 0, 0]
        
        self._move_ball()
        self._move(action)
        
        reward = 0
        game_over = False
        if self.ballpos[1] > 590:
            game_over = True
            reward = -10
            return reward, game_over, self.score
        
        if self.is_collision():
            self.ry = -self.ry
            reward = 10
            self.score += 1
            print('Score: ', self.score)
        
        self.update_ui()
        return reward, game_over, self.score
        
    def is_collision(self):
        if self.ballpos[0] >= self.barpos[0] and self.ballpos[0] <= (self.barpos[0] + BAR_SCALE*BLOCK_SIZE) and self.ballpos[1] > self.barpos[1]-BLOCK_SIZE and self.ballpos[1] < self.barpos[1] and self.new_collision:
            self.new_collision = False
            return True
        return False
                
    def _move(self, action):
        if np.array_equal(action, [1, 0, 0]):
            self.direction = 0
        elif np.array_equal(action, [0, 1, 0]):
            self.direction = RIGHT
        else:
            self.direction = LEFT
    
        if self.direction == RIGHT and self.barpos[0] < (self.w - BAR_SCALE*BLOCK_SIZE):
            self.barpos[0] = self.barpos[0]+BLOCK_SIZE
        if self.direction == LEFT and self.barpos[0] > 0:
            self.barpos[0] = self.barpos[0]-BLOCK_SIZE
            
    def _move_ball(self):
        if self.ballpos[1] <= self.barpos[1]-BLOCK_SIZE:
            self.new_collision = True
        if self.ballpos[0] < 0 or self.ballpos[0] > (self.w - BLOCK_SIZE):
            self.rx = -self.rx
        if self.ballpos[1] < 0:
            self.ry = -self.ry
        if self.move:
            self.ballpos[0] = self.ballpos[0] + self.rx
            self.ballpos[1] = self.ballpos[1] + self.ry
            
    def update_ui(self):
        self.display.fill([0,0,0])
        self.display.blit(self.ball,self.ballpos)
        self.display.blit(self.bar,self.barpos)
        pygame.display.update()