import pygame
import random
import numpy as np
from pygame import *

RIGHT = 1
LEFT = 2

BLOCK_SIZE = 10
SPEED = 40
BAR_SCALE = 8

class Game:
    
    def __init__(self,w=600,h=600):
        self.w = w
        self.h = h
        self.display = pygame.display.set_mode([self.w, self.h])
        pygame.display.set_caption('Tennis')
        self.clock = pygame.time.Clock()
        self.reset()
        self.move = True
        self.action = [1,0,0]
        
    def reset(self):
        self.direction = 0
        
        self.ball = [pygame.Surface((BLOCK_SIZE, BLOCK_SIZE))]
        self.ballpos = [[300, 400]]
        self.ball[len(self.ball)-1].fill((255, 255, 255))
        
        self.barpos = [300, 550]
        self.bar = pygame.Surface((BAR_SCALE*BLOCK_SIZE, BLOCK_SIZE))
        self.bar.fill((255, 255, 255))
        
        r = random.randint(0,1)
        if r == 0:  
            self.rx = [5]
        else:
            self.rx = [-5]
        self.ry = [random.randint(-5,-3)]
        
        self.balls = 1
        self.score = 0
        self.frame_iteration = 0
        self.new_collision = [True]
        self.added = False
        
    def step(self):
        self.frame_iteration += 1
        self.clock.tick(SPEED)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    self.action = [0, 1, 0]
                if event.key == pygame.K_LEFT:
                    self.action = [0, 0, 1]
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_RIGHT:
                    self.action = [1, 0, 0]
                if event.key == pygame.K_LEFT:
                    self.action = [1, 0, 0]
        
        self._move_ball()
        self._move()
        
        game_over = False
        
        for i in range(self.balls):
            if self.ballpos[i][1] > 590:
                game_over = True
                return game_over
        
        if self.is_collision():
            self.score += 1
            print('Score: ', self.score)
        
        if self.score%5 == 0 and self.score > 0 and self.added == False:
            self.add_ball()
            self.added = True
        if self.score%6 == 0 and self.score > 0:
            self.added = False
        
        self.update_ui()
        return game_over
    
    def add_ball(self):
        self.balls += 1
        
        self.ball.append(pygame.Surface((BLOCK_SIZE, BLOCK_SIZE)))
        self.ballpos.append([300, 400])
        self.ball[len(self.ball)-1].fill((255, 255, 255))
        
        r = random.randint(0,1)
        if r == 0:  
            self.rx.append(5)
        else:
            self.rx.append(-5)
        self.ry.append(random.randint(-5,-3))
        
        self.new_collision.append(True)
        
    def is_collision(self):
        col = False
        for i in range(self.balls):
            if self.ballpos[i][0] >= self.barpos[0] and self.ballpos[i][0] <= (self.barpos[0] + BAR_SCALE*BLOCK_SIZE) and self.ballpos[i][1] > self.barpos[1]-BLOCK_SIZE and self.ballpos[i][1] < self.barpos[1] and self.new_collision[i]:
                self.ry[i] = -self.ry[i]
                self.new_collision[i] = False
                col = True
        return col
                
    def _move(self):
        if np.array_equal(self.action, [1, 0, 0]):
            self.direction = 0
        elif np.array_equal(self.action, [0, 1, 0]):
            self.direction = RIGHT
        else:
            self.direction = LEFT
    
        if self.direction == RIGHT and self.barpos[0] < (self.w - BAR_SCALE*BLOCK_SIZE):
            self.barpos[0] = self.barpos[0]+BLOCK_SIZE
        if self.direction == LEFT and self.barpos[0] > 0:
            self.barpos[0] = self.barpos[0]-BLOCK_SIZE
            
    def _move_ball(self):
        for i in range(self.balls):
            if self.ballpos[i][1] <= self.barpos[1]-BLOCK_SIZE:
                self.new_collision[i] = True
            if self.ballpos[i][0] < 0 or self.ballpos[i][0] > (self.w - BLOCK_SIZE):
                self.rx[i] = -self.rx[i]
            if self.ballpos[i][1] < 0:
                self.ry[i] = -self.ry[i]
            if self.move:
                self.ballpos[i][0] = self.ballpos[i][0] + self.rx[i]
                self.ballpos[i][1] = self.ballpos[i][1] + self.ry[i]
            
    def update_ui(self):
        self.display.fill([0,0,0])
        for i in range(self.balls):
            self.display.blit(self.ball[i],self.ballpos[i])
        self.display.blit(self.bar,self.barpos)
        pygame.display.update()

game = Game()
done = False
while not done:
    done = game.step()
    if done:
        ans = input('Want to play again?(y/n)')
        if ans == 'y' or ans == 'Y':
            game.reset()
            done = False
pygame.quit()
quit()