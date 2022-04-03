import random

import os
import time

from numpy import true_divide

"""
2PX3 Highway Simulation Starting Code 

Simulation for a fast/slow highway driver. Modelling choices:
1) Cars will cruise via their speed and safe follow distance
2) If a car cannot maintain its speed, it will desire to change lanes

See the video for more detail.

Dr. Vincent Maccio 2022-02-01 
"""

EMPTY = " "
#You can think of these speeds as 125 and 100 km/hr
FAST = 5
SLOW = 4
SAFE_FOLLOW = 4
LEFT = 0
RIGHT = 1
CRUISE = "Cruise"
LANE_CHANGE = "Lane Change"
OFFSET = 5 #The last OFFSET indices of the road are not considered to avoid out of bounds errors
CAR_PROBABILITY = 0.75
FAST_PROBABILITY = 0.5
PRINT_ROAD = True
HIGHWAY_LENGTH = 150
AUTONOMOUS_SPEED = 4
AUTONOMOUS_PROBABILITY = 0.5

class Driver:

    def __init__(self, speed, arrive_time, autonomous):
        self.desired_speed = speed
        self.speed = speed
        self.safe_follow = SAFE_FOLLOW
        self.desire = CRUISE
        self.arrive_time = arrive_time
        self.autonomous = autonomous


class Highway:

    def __init__(self, length):
        self.road = [[], []]
        self.length = length
        for _ in range(length):
            self.road[0].append(EMPTY)
            self.road[1].append(EMPTY)
        
    def can_lane_change(self, lane, i):
        return

    def get(self, lane, index):
        return self.road[lane][index]

    def set(self, lane, index, value):
        self.road[lane][index] = value

    #Returns the distance until the next car, from index i within k; returns k if all spots are EMPTY
    def safe_distance_within(self, lane, index, k):
        x = 0
        for i in range(index + 1, index + k + 1):
            if i >= self.length:
                return k
            if self.road[lane][i] != EMPTY:
                return x
            x += 1
        return x

    def safe_lane_change(self, lane, i):
        return self.road[lane][i] == EMPTY and self.road[lane][i+1] == EMPTY and self.road[lane][i+2] == EMPTY

    def safe_lane_distance(self, lane, i):
        driver = self.get(1-lane, i)
        for j in range(driver.speed):
            if i + j >= self.length:
                return True
            elif self.road[lane][i + j] != EMPTY:
                return False
        return True

    def print(self):
        s = "\n"
        
        for i in range(self.length):
            s += "="
        
        s += "\n"
        
        for i in range(self.length):
            if self.road[LEFT][i] == EMPTY:
                s += " "
            elif self.road[LEFT][i].autonomous:
                s += 'A'
            else:
                s += str(self.get(LEFT, i).speed)
        s += "\n"

        for i in range(self.length):
            if i%2 == 0:
                s += " "
            else:
                s += "-"

        s += "\n"
        
        for i in range(self.length):
            if self.road[RIGHT][i] == EMPTY:
                s += " "
            elif self.road[RIGHT][i].autonomous:
                s += 'A'
            else:
                s += str(self.get(RIGHT, i).speed)

        s += "\n"

        for i in range(self.length):
            s += "="
        
        s += "\n"
        
        #input()
        os.system("cls")
        print(s)
        time.sleep(0.02)
        


class Simulation:

    def __init__(self, time_steps):
        self.road = Highway(HIGHWAY_LENGTH)
        self.time_steps = time_steps
        self.current_step = 0
        self.data = []
        self.collisions = 0

    def run(self):
        while self.current_step < self.time_steps:
            self.execute_time_step()
            self.current_step += 1
            if PRINT_ROAD:
                self.road.print()

    def execute_time_step(self):
        for i in range(self.road.length - 1, -1, -1):
            if self.road.get(LEFT, i) != EMPTY:
                self.sim_left_driver(i)
            if self.road.get(RIGHT, i) != EMPTY:
                self.sim_right_driver(i)
            
        for i in range(0, self.road.length - 3, 1):
            if self.road.get(LEFT, i) != EMPTY:
                if self.road.get(LEFT, i).autonomous:
                    self.adjust_speed(LEFT, i)
            if self.road.get(RIGHT, i) != EMPTY:
                if self.road.get(RIGHT, i).autonomous:
                    self.adjust_speed(RIGHT, i)
    
        self.gen_new_drivers()

    def sim_right_driver(self, i):
        driver = self.road.get(RIGHT, i)
        if max(driver.speed, 3) + i >= self.road.length - 1:
            self.road.set(RIGHT, i, EMPTY)
            self.data.append(self.current_step - driver.arrive_time)
            return #Car reaches the end of the highway

        if driver.desire == LANE_CHANGE:
            if self.road.safe_lane_change(LEFT, i):
                self.road.set(LEFT, i, driver)
                self.road.set(RIGHT, i, EMPTY)
                driver.desire = CRUISE
                self.sim_cruise(LEFT, i)
            else:
                self.sim_cruise(RIGHT, i)
        elif driver.desire == CRUISE:
            self.sim_cruise(RIGHT, i)

    def sim_left_driver(self, i):
        driver = self.road.get(LEFT, i)
        if max(driver.speed, 3) + i >= self.road.length - 1:
            self.road.set(LEFT, i, EMPTY)
            self.data.append(self.current_step - driver.arrive_time)
            return #Car reaches the end of the highway

        if driver.desire == LANE_CHANGE:
            if self.road.safe_lane_change(RIGHT, i):
                self.road.set(RIGHT, i, driver)
                self.road.set(LEFT, i, EMPTY)
                driver.desire = CRUISE
                self.sim_cruise(RIGHT, i)
            else:
                self.sim_cruise(LEFT, i)
        elif driver.desire == CRUISE:
            self.sim_cruise(LEFT, i)

    def sim_cruise(self, lane, i):
        driver = self.road.get(lane, i)
        x = self.road.safe_distance_within(lane, i, driver.speed + driver.safe_follow)

        self.road.set(lane, i, EMPTY)

        if x >= driver.speed + driver.safe_follow:
            if not driver.autonomous:
                if driver.speed < driver.desired_speed:
                    driver.speed += 1
            self.road.set(lane, i + driver.speed, driver) #Car moves forward by full speed
        elif x > driver.safe_follow:
            driver.desire = LANE_CHANGE
            if driver.speed > 1:
                driver.speed -= 1
            else: 
                driver.speed = 1
            if self.road.get(lane, i + driver.speed) != EMPTY:
                self.collision(lane, i)
                self.road.set(lane, i + driver.speed - 1, driver)
                self.road.get(lane, i + driver.speed - 1).speed = 1
            else:
                self.road.set(lane, i + driver.speed, driver) #Car moves forward just enough to maintain safe_distance
        else:
            driver.desire = LANE_CHANGE
            if driver.speed > 0:
                driver.speed -= 1
            if self.road.get(lane, i + driver.speed) != EMPTY:
                self.collision(lane, i)
                self.road.set(lane, i + driver.speed - 1, driver)
                self.road.get(lane, i + driver.speed - 1).speed = 1
            else:
                self.road.set(lane, i + driver.speed, driver) #Car moves forward by just 1 spot

    def adjust_speed(self, lane, i):
        driver = self.road.get(lane, i)
        if (lane == RIGHT):
            if not self.road.safe_lane_distance(LEFT, i):
                driver.speed -= 2
            elif driver.speed < driver.desired_speed:
                driver.speed += 1
        elif (lane == LEFT):
            if not self.road.safe_lane_distance(RIGHT, i):
                if (self.road.get(RIGHT, i) != EMPTY and self.road.get(RIGHT, i).autonomous): #prevents autonomous blockcade case
                    driver.speed += 1
                else:
                    driver.speed -= 2
            elif driver.speed < driver.desired_speed:
                driver.speed += 1

    def collision(self, lane, i):
        print("COLLISION")
        self.collisions += 1

    def gen_new_drivers(self):
        r = random.random()
        if self.road.get(LEFT, 0) == EMPTY and r < CAR_PROBABILITY:
            r = random.random()
            if r < AUTONOMOUS_PROBABILITY:
                driver = Driver(AUTONOMOUS_SPEED, self.current_step, True)
                self.road.set(LEFT, 0, driver)
                x = self.road.safe_distance_within(LEFT, 0, driver.speed + driver.safe_follow)
                if x < driver.speed:
                    driver.speed = x
            else:
                r = random.random()
                if r < FAST_PROBABILITY:
                    driver = Driver(FAST, self.current_step, False)
                    self.road.set(LEFT, 0, driver)
                    x = self.road.safe_distance_within(LEFT, 0, driver.speed + driver.safe_follow)
                    if x < driver.speed:
                        driver.speed = x
                else:
                    driver = Driver(SLOW, self.current_step, False)
                    self.road.set(LEFT, 0, driver)
                    x = self.road.safe_distance_within(LEFT, 0, driver.speed + driver.safe_follow)
                    if x < driver.speed:
                        driver.speed = x

        r = random.random()
        if self.road.get(RIGHT, 0) == EMPTY and r < CAR_PROBABILITY:
            r = random.random()
            if r < AUTONOMOUS_PROBABILITY:
                driver = Driver(AUTONOMOUS_SPEED, self.current_step, True)
                self.road.set(RIGHT, 0, driver)
                x = self.road.safe_distance_within(RIGHT, 0, driver.speed + driver.safe_follow)
                if x < driver.speed:
                    driver.speed = x
            else:
                r = random.random()
                if r < FAST_PROBABILITY:
                    driver = Driver(FAST, self.current_step, False)
                    self.road.set(RIGHT, 0, driver)
                    x = self.road.safe_distance_within(RIGHT, 0, driver.speed + driver.safe_follow)
                    if x < driver.speed:
                        driver.speed = x
                else:
                    driver = Driver(SLOW, self.current_step, False)
                    self.road.set(RIGHT, 0, driver)
                    x = self.road.safe_distance_within(RIGHT, 0, driver.speed + driver.safe_follow)
                    if x < driver.speed:
                        driver.speed = x

    def average_time(self):
        return sum(self.data)/len(self.data)

if __name__ == "__main__":
    x = input("Number of simulations: ")
    sim = Simulation(int(x))
    sim.run()
    print("Average time: ", sim.average_time())
    print("Collisions:   ", sim.collisions)
