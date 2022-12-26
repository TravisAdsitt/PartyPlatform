## 
#   This program is meant to be a quick exploration of a preference system for
#   simulating individuals in a town.
#
#   Author: Travis Adsitt
##

from dataclasses import dataclass, field
import random
from typing import List


class IDManager:
    id = 0
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(IDManager, cls).__new__(cls)
            return cls.instance
    
    @classmethod
    def getNewID(cls):
        cls.id += 1
        
        return cls.id
        

class Person:
    def __init__(self, preference_width: int, move_threshold: float = None):
        self.id = IDManager.getNewID()
        self.preference_width = preference_width
        # UINT8 bitfield for preferences
        self.preference_base_bits = random.getrandbits(self.preference_width) 
        # Are we basically happy or sad?
        self.basically_happy = bool(random.getrandbits(1))
        # Set a random happiness threshold in a range if None
        if move_threshold == None:
            self.move_threshold = random.randint(40, 60) / 100
        else:
            self.move_threshold = move_threshold
        # Set persons money
        self.money = 0

        # Setup our unbendables
        self._set_unbendable_preferences_()

    def _set_unbendable_preferences_(self):
        # How many bits will be considered in the happiness calculation
        self.hardheadedness = random.randint(0, self.preference_width - 1) 
        # Bitmask to store our unbendable preferences
        self.unbendable_bitmask = 0

        bits_set = 0
        while bits_set < self.hardheadedness:
            # Set a random bit
            random_bit = 1 << random.randint(0, self.preference_width - 1)

            # If it isn't already set add this bit to our unbendables
            if not bool(self.unbendable_bitmask & random_bit):
                self.unbendable_bitmask |= random_bit
                bits_set += 1
    
    def vote(self):
        return self.preference_base_bits
    
    def check_happiness(self, environment_value: int):
        # Set the base level of happiness
        hapinness = self.preference_width if self.basically_happy else 0

        # Step through all the bits in our preference width
        for bit in range(0, self.preference_width):
            if self.unbendable_bitmask & (1 << bit):
                preference_bit = (self.preference_base_bits >> bit) & 1
                environment_bit = (environment_value >> bit) & 1

                if preference_bit != environment_bit:
                    hapinness -= 1
                
                if preference_bit == environment_bit:
                    hapinness += 1
        
        if hapinness > self.preference_width:
            hapinness = self.preference_width
        elif hapinness < 0:
            hapinness = 0
        
        return hapinness
    
    def is_happy(self, environment_value: int):
        return bool((self.check_happiness(environment_value) / 8) > self.move_threshold)

    def wants_to_move(self, from_env: int, to_env: int):
        happinness_from = self.check_happiness(from_env) / self.preference_width
        happinness_to = self.check_happiness(to_env) / self.preference_width

        return bool(happinness_from < self.move_threshold) and bool(happinness_to > happinness_from)

    def can_move(self, cost: int = 20):
        return bool(self.money - cost > 0)

@dataclass
class TownPersonStatus:
    earned_ytd: int
    seniority: float

class Town:
    def __init__(self, town_pop_max: int, town_pop_min: int = 0, platform_width: int = 8, starting_wealth_per_person: int = 100, utility_rate: int = 0.1, income_tax_rate: int = 0.36):
        
        self.starting_population = random.randint(town_pop_min, town_pop_max)
        self.id = IDManager.getNewID()
        self.platform_width = platform_width
        self.starting_wealth_per_person = starting_wealth_per_person
        self.starting_bank = self.starting_population * self.starting_wealth_per_person
        self.town_bank = self.starting_bank
        self.income_town_tax_rate = income_tax_rate
        self.town_utility_rate = utility_rate
        self.people_status = {}
        self.people = []
        

        self._init_population_(self.starting_population)
        self.vote_for_platform()
    
    @property
    def utility_per_person(self):
        return self.average_wealth * self.town_utility_rate

    @property
    def population(self):
        return len(self.people)

    def _init_population_(self, initial_population: int):
        for _ in range(initial_population):
            new_person = Person(self.platform_width)
            # Keep track of how long people have lived here
            self.people_status[new_person.id] = TownPersonStatus(0, random.randint(0, 25) / 100)
            self.people.append(new_person)
    
    def get_person_with_id(self, id: int):
        for person in self.people:
            if person.id == id:
                return person
        
        return None

    def calculate_base_rate_taxes(self, person_status: TownPersonStatus):
        taxes = self.income_town_tax_rate * person_status.earned_ytd
        utilities = self.utility_per_person * person_status.seniority

        return taxes + utilities

    def step_town(self, tax_step: bool = False):
        for person in self.people:
            if person.id not in self.people_status:
                self.people_status[person.id] = TownPersonStatus(0, 0)

            if self.people_status[person.id].seniority < 1:
                self.people_status[person.id].seniority += 0.01

        random_order_keys = list(self.people_status.keys())
        random.shuffle(random_order_keys)

        for person in random_order_keys:
            person_obj = self.get_person_with_id(person)
            
            if person_obj is None:
                continue

            step_loss = min(self.town_bank, self.people_status[person].seniority)
            tax_calculation = self.calculate_base_rate_taxes(self.people_status[person]) * (person_obj.money / self.get_total_wealth())

            self.people_status[person].earned_ytd += step_loss if not tax_step else 0
            person_obj.money += step_loss if not tax_step else -tax_calculation
            self.town_bank -= step_loss if not tax_step else -tax_calculation

            if tax_step:
                self.people_status[person].earned_ytd = 0
            


    def get_total_wealth(self, include_bank: bool = True):
        return round(sum([person.money for person in self.people]), 2) + (self.town_bank if include_bank else 0)
    
    @property
    def average_wealth(self):
        return round(self.get_total_wealth(False) / len(self.people), 2)

    def vote_for_platform(self):
        if not self.people:
            return
        
        votes = [0 for _ in range(self.platform_width)]

        for person in self.people:
            vote = person.vote()

            for bit in range(self.platform_width):
                bit_vote = (vote >> bit) & 1

                if bit_vote > 0:
                    votes[bit] += 1
                else:
                    votes[bit] -= 1
        
        platform = 0

        for bit in range(self.platform_width):
            if votes[bit] > 0:
                platform |= 1 << bit
        
        self.town_platform = platform

    def get_movers(self):
        movers = []

        for person in self.people:
            if not person.is_happy(self.town_platform):
                movers.append(person)

        for mover in movers:
            self.people.remove(mover)
        
        return movers

@dataclass
class MovingGroup:
    from_town: Town
    people: List[Person]

@dataclass
class TownDemand:
    town: Town
    num_people_want: int = 0
    num_people_leaving: int = 0

    def get_move_cost_adjustment(self):
        total_movement = self.num_people_want + self.num_people_leaving
        movement_delta = self.num_people_want - self.num_people_leaving
        return 1 + (movement_delta / total_movement)

@dataclass
class MovingMarket:
    base_moving_cost: int
    town_demand: List[TownDemand] = field(default_factory=list)

    @property
    def moving_costs(self):
        town_moving_costs = []

        for td in self.town_demand:
            town_moving_costs.append(self.get_town_moving_cost(td.town))
        
        return town_moving_costs

    def get_town_moving_cost(self, town: Town):
        for td in self.town_demand:
            if td.town == town:
                return max(self.base_moving_cost * td.get_move_cost_adjustment(), self.base_moving_cost)

@dataclass
class WorldStepInfo:
    number_people_moved: int
    number_people_desire_moved: int
    current_market: MovingMarket

class World:
    def __init__(self, num_towns: int = 5, steps_in_year: int = 10, years_to_vote: int = 4):
        self.towns = [Town(1000) for _ in range(num_towns)]
        self.steps_in_year = steps_in_year
        self.years_to_vote = years_to_vote
        self.current_step = 0
    
    def step_world(self) -> WorldStepInfo:
        for town in self.towns:
            # Boolean check if it is a taxes taxes are being taken
            town.step_town(bool((self.current_step % self.steps_in_year) == 0))

        # Voting year?
        if (self.current_step % (self.steps_in_year * self.years_to_vote)) == 0:
            for town in self.towns:
                town.vote_for_platform()

        move_info = self.move_people()

        self.current_step += 1

        return move_info

    def move_people(self):
        base_moving_cost = 50
        total_number_people_moved = 0
        total_number_want_moved = 0

        # Initialize Market
        current_market = MovingMarket(base_moving_cost)

        # Initialize Demand Objects
        for town in self.towns:
            current_market.town_demand.append(TownDemand(town))

        # Initialize Moving Groups
        moving_groups: List[MovingGroup] = []
        for town in self.towns:
            moving_groups.append(MovingGroup(town, town.get_movers()))

        # Set Town Demand and Loss
        for moving_group in moving_groups:
            for td in current_market.town_demand:
                # Count the people wanting to leave
                if td.town == moving_group.from_town:
                    td.num_people_leaving = len(moving_group.people)
                    continue
                
                # Count the people who want to come
                for person in moving_group.people:
                    if person.wants_to_move(moving_group.from_town.town_platform, td.town.town_platform):
                        td.num_people_want += 1
                
        # Move or Not
        for moving_group in moving_groups:
            other_towns = [town for town in self.towns if town != moving_group.from_town]
            random.shuffle(other_towns)

            for person in moving_group.people:
                person_moved = False
                for town in other_towns:
                    if person.wants_to_move(moving_group.from_town.town_platform, town.town_platform):
                        total_number_want_moved += 1
                        if  person.money > current_market.get_town_moving_cost(town):
                            moving_cost = current_market.get_town_moving_cost(town)
                            person.money -= moving_cost
                            town.town_bank += moving_cost
                            total_number_people_moved += 1
                            town.people.append(person)
                            person_moved = True
                            break
                
                # If we couldn't move them... well they stay then
                if not person_moved:
                    moving_group.from_town.people.append(person)

        return WorldStepInfo(total_number_people_moved, total_number_want_moved, current_market)

    def __str__(self):
        ret_str = "WORLD STATS:\n"

        for town in self.towns:
            ret_str += str(town)

        return ret_str




if __name__ == "__main__":
    world = World()

    while True:
        world.step_world()
        print(world)
        input()