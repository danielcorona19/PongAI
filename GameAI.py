import numpy as np
from collections import deque
import random
import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import matplotlib.pyplot as plt
from Game import Game

MAX_MEMORY = 100_000
BATCH_SIZE = 1_000
LR = 1e-3

class LinearQNet(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super().__init__()
        self.linear1 = nn.Linear(input_size, hidden_size)
        self.linear2 = nn.Linear(hidden_size, output_size)

    def forward(self, x):
        x = F.relu(self.linear1(x))
        x = self.linear2(x)
        return x
    
class Trainer:
    def __init__(self, model, lr, gamma):
        self.model = model
        self.lr = lr
        self.gamma = gamma
        self.epsilon = 0
        self.optimizer = optim.Adam(model.parameters(), lr=self.lr)
        self.criterion = nn.MSELoss()
        
    def step(self, state, action, reward, next_state, done):
        state = torch.tensor(state, dtype=torch.float)
        next_state = torch.tensor(next_state, dtype=torch.float)
        action = torch.tensor(action, dtype=torch.float)
        reward = torch.tensor(reward, dtype=torch.float)
        
        if len(state.shape) == 1:
            state = torch.unsqueeze(state, 0)
            next_state = torch.unsqueeze(next_state, 0)
            action = torch.unsqueeze(action, 0)
            reward = torch.unsqueeze(reward, 0)
            done = (done, )
        
        pred = self.model(state)
        
        target = pred.clone()
        
        for i in range(len(done)):
            Q_new = reward[i]
            if not done[i]:
                Q_new = reward[i] + self.gamma*torch.max(self.model(next_state[i]))
            
            target[i][torch.argmax(action).item()] = Q_new
        
        self.optimizer.zero_grad()
        loss = self.criterion(target, pred)
        loss.backward()
        
        self.optimizer.step()
        
class Agent:
    def __init__(self):
        self.n_games = 0
        self.gamma = 0.9
        self.model = LinearQNet(3, 256, 3)
        self.trainer = Trainer(self.model, lr=LR, gamma=self.gamma)
        self.memory = deque(maxlen=MAX_MEMORY)
    
    def get_state(self, game):
        pos = game.barpos[0]
        dist_x = game.ballpos[0] - game.barpos[0]
        dist_y = abs(game.ballpos[1] - game.barpos[1])
        state = [pos, dist_x, dist_y]
        
        return np.array(state, dtype=int)
    
    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))
       
    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE) # list of tuples
        
        else:
            mini_sample = self.memory
        
        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.trainer.step(states, actions, rewards, next_states, dones)
        
    def train_short_memory(self, state, action, reward, next_state, done):
        self.trainer.step(state, action, reward, next_state, done)
        
    def get_action(self, state):
        # random moves: tradeoff exploration / explotation
        self.epsilon = 40 - self.n_games/2
        final_move = [0, 0, 0]
        if random.randint(0, 200) < self.epsilon:
            move = random.randint(0, 2)
            final_move[move] = 1
        
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            move = torch.argmax(prediction).item()
            final_move[move] = 1

        return final_move
        
def train():
    plot_scores = []
    plot_mean_scores = []
    total_score = 0
    record = 0
    agent = Agent()
    game = Game()
    
    while True:
        state_old = agent.get_state(game)
        final_move = agent.get_action(state_old)
        
        reward, done, score = game.step(final_move)
        state_new = agent.get_state(game)
        
        agent.train_short_memory(state_old, final_move, reward, state_new, done)
        
        agent.remember(state_old, final_move, reward, state_new, done)
        
        if done:
                game.reset()
                agent.n_games += 1
                agent.train_long_memory()
    
                if score > record:
                    record = score
                    #agent.model.save()
                
                print("Game: ", agent.n_games, " Score: ", score, "Record: ", record)
    
                plot_scores.append(score)
                total_score += score
                mean_score = total_score / agent.n_games
                plot_mean_scores.append(mean_score)
            

train()