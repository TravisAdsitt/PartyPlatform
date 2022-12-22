## 
#   This program is meant to be a quick exploration of a preference system for
#   simulating individuals in a town.
#
#   Author: Travis Adsitt
##

from dataclasses import dataclass
import random


class Person:
    def __init__(self, preference_width: int, move_threshold: float = None):
        self.preference_width = preference_width
        # UINT8 bitfield for preferences
        self.preference_base_bits = random.getrandbits(self.preference_width) 
        # Are we basically happy or sad?
        self.basically_happy = bool(random.getrandbits(1))
        # Set a random threshold in a range if None
        if move_threshold == None:
            self.move_threshold = random.randint(40, 60) / 100
        else:
            self.move_threshold = move_threshold


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
        
        return hapinness
    
    def wants_to_move(self, environment_value: int):
        happinness = self.check_happiness(environment_value) / self.preference_width

        return bool(happinness < self.move_threshold)

class Town:
    def __init__(self, town_pop_max: int, town_pop_min: int = 0, platform_width: int = 32):
        self.population = random.randint(town_pop_min, town_pop_max)
        self.platform_width = platform_width
        self.people = []

        self._init_population_()
        self.vote_for_platform()

    
    def _init_population_(self):
        for _ in range(self.population):
            self.people.append(Person(self.platform_width))
    
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
    
    def add_person(self, new_person: Person):
        self.people.append(new_person)

    def get_movers(self):
        movers = []

        for person in self.people:
            if person.wants_to_move(self.town_platform):
                movers.append(person)

        for mover in movers:
            self.people.remove(mover)
        
        return movers

    def visit(self, person: Person):
        return person.check_happiness(self.town_platform)

    def __str__(self):
        return f"TOWN PLATFORM: {bin(self.town_platform)[2:]} ({hex(self.town_platform)}) TOWN POPULATION: {len(self.people)}\n"


@dataclass
class WorldStepInfo:
    number_people_moved: int

class World:
    def __init__(self, num_towns: int = 10):
        self.towns = [Town(1000) for _ in range(num_towns)]
        self.steps_in_year = 10
        self.years_to_vote = 4
        self.current_year = 0
    
    def step_world(self) -> WorldStepInfo:
        total_number_people_moved = 0
        towns_and_movers = []
        
        for town in self.towns:
            towns_and_movers.append(town.get_movers())
        
        for group_index, moving_group in enumerate(towns_and_movers):
            other_towns = [town for i, town in enumerate(self.towns) if i != group_index]

            random.shuffle(moving_group)
            # Move by preference
            while moving_group:
                current_person = moving_group.pop(0)

                happiest_town = self.towns[group_index]
                happiness_score = self.towns[group_index].visit(current_person)

                for town in other_towns:
                    happiness_check = town.visit(current_person)
                    if happiness_score < happiness_check:
                        happiest_town = town
                        happiness_score = happiness_check
                
                if happiest_town != self.towns[group_index]:
                    total_number_people_moved += 1

                happiest_town.people.append(current_person)
                        

            # Random town selection
            # while moving_group:
            #     current_person = moving_group.pop(0)
            #     chosen_town = random.choice(other_towns)
            #     chosen_town.add_person(current_person)
            #     total_number_people_moved += 1
        
        if self.current_year % (self.steps_in_year * self.years_to_vote) == 0:
            for town in self.towns:
                town.vote_for_platform()
        
        self.current_year += 1

        return WorldStepInfo(total_number_people_moved)
    
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