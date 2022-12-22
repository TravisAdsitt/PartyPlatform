from kivy_garden.graph import Graph, MeshLinePlot
from kivy.properties import ObjectProperty
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.gridlayout import GridLayout
from kivy.app import App
import random
from simulationobjects import World


class PopulationGraph(RelativeLayout):
    pop_graph = ObjectProperty(None)

    def __init__(self, num_towns: int):
        super().__init__()
        randint = random.randint

        self.population_lists = [[] for _ in range(num_towns)]
        self.plots = [MeshLinePlot(color=[randint(0,100) / 100, randint(0,100) / 100, randint(0,100) / 100, 1]) for _ in range(num_towns)]
        self.moved_list = []

        for plot in self.plots:
            self.pop_graph.add_plot(plot)

        Clock.schedule_interval(self.update_graph, 1/30)
        

    def update_graph(self, dt):
        for i, plot in enumerate(self.plots):
            start_index = 0 if len(self.population_lists[i]) < 20 else -10
            # Assemble and set the points
            plot.points = [(i, pop) for i, pop in enumerate(self.population_lists[i][start_index:])]
            # Extend the plots max x
            self.pop_graph.xmax = len(self.population_lists[i][start_index:]) + 1

class PeopleMovedGraph(RelativeLayout):
    mov_graph = ObjectProperty(None)

    def __init__(self):
        super().__init__()
        randint = random.randint

        self.plot = MeshLinePlot(color=[randint(0,100) / 100, randint(0,100) / 100, randint(0,100) / 100, 1])
        self.moved_list = []

        self.mov_graph.add_plot(self.plot)

        Clock.schedule_interval(self.update_graph, 1/30)
        

    def update_graph(self, dt):
        start_index = 0 if len(self.moved_list) < 20 else -10
        # Assemble and set the points
        self.plot.points = [(i, num_moved) for i, num_moved in enumerate(self.moved_list[start_index:])]

        # Extend the plots max x
        self.mov_graph.xmax = len(self.moved_list[start_index:]) + 1
        self.mov_graph.ymax = max(self.moved_list[start_index:]) + 10
        self.mov_graph.ymin = min(self.moved_list[start_index:]) - 10

class PartyPlatformApp(App):
    def __init__(self):
        super().__init__()
        self.world = World()
        Clock.schedule_interval(self.step_sim, 1/60)

    def step_sim(self, dt):
        step_info = self.world.step_world()

        for town_index in range(len(self.world.towns)):
            self.population_graph.population_lists[town_index].append(len(self.world.towns[town_index].people))

        self.movers_graph.moved_list.append(step_info.number_people_moved)

    def build(self):
        grid = GridLayout(cols=2)

        self.population_graph = PopulationGraph(len(self.world.towns))
        self.movers_graph = PeopleMovedGraph()

        grid.add_widget(self.population_graph)
        grid.add_widget(self.movers_graph)

        return grid

if __name__ == "__main__":
    PartyPlatformApp().run()