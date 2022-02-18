import pygame
import random
import numpy as np
import neat
import math
import os
from pygame import *

RIGHT = 1
LEFT = 2

BLOCK_SIZE = 10
SPEED = 50
BAR_SCALE = 5

class Game:
    
    def __init__(self,genomes, config, w=600, h=600):
        self.w = w
        self.h = h
        self.display = pygame.display.set_mode([self.w, self.h])
        pygame.display.set_caption('Pong')
        self.clock = pygame.time.Clock()
        self.ballspos = []
        self.barspos = []
        self.balls =[]
        self.bars = []
        self.rx = []
        self.ry = []
        self.ge = []
        self.nets = []
        self.colors = []
        self.new_collision = []
        self.reset(genomes, config)
        self.move = True
        
    def create_ball(self, color):
        self.ballspos.append([300, 400])
        self.balls.append(pygame.Surface((BLOCK_SIZE, BLOCK_SIZE)))
        self.balls[len(self.balls)-1].fill((color[0], color[1], color[2]))
        self.rx.append(random.randint(0,1))
        if self.rx[len(self.rx)-1] == 0:
            self.rx[len(self.rx)-1] = 5
        else:
            self.rx[len(self.rx)-1] = -5
        self.ry.append(random.randint(-5,-3))
    
    def create_bar(self, color):
        self.barspos.append([300, 550])
        self.bars.append(pygame.Surface((BAR_SCALE*BLOCK_SIZE, BLOCK_SIZE)))
        self.bars[len(self.bars)-1].fill((color[0], color[1], color[2]))
        
    def reset(self, genomes, config):
        self.direction = 0
        self.scores = []
        
        for genome_id, genome in genomes:
            color = [random.randint(0,255), random.randint(0,255), random.randint(0,255)]
            self.colors.append(color)
            self.create_bar(color)
            self.create_ball(color)
            self.new_collision.append(True)
            self.ge.append(genome)
            net = neat.nn.FeedForwardNetwork.create(genome, config)
            self.nets.append(net)
            genome.fitness = 0
            self.scores.append(0)
        
        self.frame_iteration = 0
        
    def step(self):
        self.frame_iteration += 1
        self.clock.tick(SPEED)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        
        self._move_ball()
        self._move()
        
        idxs_remove = []
        for i in range(len(self.balls)):
            if self.ballspos[i][1] > self.h - BLOCK_SIZE:
                idxs_remove.append(i)

        for j in range(len(idxs_remove)):
            i = idxs_remove[j] - j
            self.remove(i)
                
        self.is_collision()
        
        self.update_ui()
        
        return len(self.bars)
        
    def remove(self, i):
        self.ge[i].fitness -= 1
        self.ballspos.pop(i)
        self.balls.pop(i)
        self.bars.pop(i)
        self.barspos.pop(i)
        self.ge.pop(i)
        self.nets.pop(i)
        self.colors.pop(i)
        self.rx.pop(i)
        self.ry.pop(i)
        self.new_collision.pop(i)
        
    def is_collision(self):
        for i in range(len(self.balls)):
            if self.ballspos[i][0] >= self.barspos[i][0] and self.ballspos[i][0] <= (self.barspos[i][0] + BAR_SCALE*BLOCK_SIZE) and self.ballspos[i][1] > self.barspos[i][1]-BLOCK_SIZE and self.ballspos[i][1] < self.barspos[i][1] and self.new_collision[i]:
                self.ry[i] = -self.ry[i]
                self.new_collision[i] = False
                self.scores[i] += 1
                
    def _move(self):
        for i in range(len(self.bars)):
            action = self.nets[i].activate((self.ballspos[i][0]-self.barspos[i][0], abs(self.ballspos[i][1] - self.barspos[i][1])))
            
            if action[0] > 0.5:
                self.direction = RIGHT
            else:
                self.direction = LEFT
        
            if self.direction == RIGHT and self.barspos[i][0] < (self.w - BAR_SCALE*BLOCK_SIZE):
                self.barspos[i][0] = self.barspos[i][0]+BLOCK_SIZE
            if self.direction == LEFT and self.barspos[i][0] > 0:
                self.barspos[i][0] = self.barspos[i][0]-BLOCK_SIZE
            
    def _move_ball(self):
        for i in range(len(self.balls)):
            if self.ballspos[i][1] <= self.barspos[i][1]-BLOCK_SIZE:
                self.new_collision[i] = True
            if self.ballspos[i][0] < 0 or self.ballspos[i][0] > (self.w - BLOCK_SIZE):
                self.rx[i] = -1.001*self.rx[i]
            if self.ballspos[i][1] < 0:
                self.ry[i] = -1.001*self.ry[i]
            if self.move:
                self.ballspos[i][0] = self.ballspos[i][0] + self.rx[i]
                self.ballspos[i][1] = self.ballspos[i][1] + self.ry[i]
            
    def update_ui(self):
        pygame.init()
        self.display.fill([0,0,0])
        
        FONT = pygame.font.Font('freesansbold.ttf', 15)
        text_1 = FONT.render(f'Bars Alive: {str(len(self.bars))}', True, (255,255,255))
        text_2 = FONT.render(f'Generation: {pop.generation+1}', True, (255,255,255))
        text_3 = FONT.render(f'Max Score: {str(max(self.scores))}', True, (255,255,255))
        
        self.display.blit(text_1, (20, 20))
        self.display.blit(text_2, (20, 50))
        self.display.blit(text_3, (20, 80))
        
        for i in range(len(self.balls)):
            self.display.blit(self.balls[i],self.ballspos[i])
            self.display.blit(self.bars[i],self.barspos[i])
            pygame.draw.line(self.display, (self.colors[i][0], self.colors[i][1], self.colors[i][2]), (self.barspos[i][0] + 25, self.barspos[i][1] + 5), (self.ballspos[i][0] + 5, self.ballspos[i][1] + 5), 2)
        pygame.display.update()

def main(genomes, config):
    game = Game(genomes=genomes, config=config)
    
    while True:
        if not game.step():
            break

def run(config_path):
    global pop
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)
    pop = neat.Population(config)
    pop.run(main,50)

local_dir = os.path.dirname(__file__)
config_path = os.path.join(local_dir, 'config.txt')
run(config_path)