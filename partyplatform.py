from typing import List
from kivy_garden.graph import Graph, MeshLinePlot, LinePlot
from kivy.properties import ObjectProperty
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.app import App
from kivy.uix.label import Label
import random
from simulationobjects import World


class PopulationGraph(RelativeLayout):
    pop_graph = ObjectProperty(None)

    def __init__(self, town_colors: List[List[int]]):
        super().__init__()
        num_towns = len(town_colors)

        self.population_lists = [[] for _ in range(num_towns)]
        self.plots = [LinePlot(color=town_color, line_width=2) for town_color in town_colors]

        for plot in self.plots:
            self.pop_graph.add_plot(plot)

        

    def update_graph(self):
        max_y = 0
        min_y = -1
        for i, plot in enumerate(self.plots):
            start_index = 0 # if len(self.population_lists[i]) < 100 else -100
            # Assemble and set the points
            plot.points = [(i, pop) for i, pop in enumerate(self.population_lists[i][start_index:])]
            max_y = max(max_y, max(self.population_lists[i]))
            if min_y < 0:
                min_y = min(self.population_lists[i])
            else:
                min_y = min(min_y, min(self.population_lists[i]))
        
        self.pop_graph.xmax = len(self.population_lists[0][start_index:]) + 1
        self.pop_graph.x_ticks_major = self.pop_graph.xmax // 10
        self.pop_graph.x_ticks_minor = self.pop_graph.xmax // 100
        self.pop_graph.ymax = max_y + 10
        self.pop_graph.ymin = min_y - 10


class PeopleMovedGraph(BoxLayout):
    mov_graph = ObjectProperty(None)
    want_mov_graph = ObjectProperty(None)

    def __init__(self):
        super().__init__()
        self.orientation = "vertical"
        randint = random.randint

        self.moved_plot = LinePlot(color=[randint(0,100) / 100, randint(0,100) / 100, randint(0,100) / 100, 1], line_width=2)
        self.want_to_move_plot = LinePlot(color=[randint(0,100) / 100, randint(0,100) / 100, randint(0,100) / 100, 1], line_width=2)

        self.want_to_move_list = []
        self.moved_list = []

        self.mov_graph.add_plot(self.moved_plot)
        self.want_mov_graph.add_plot(self.want_to_move_plot)
        
    def update_graph(self):
        start_index = 0 # if len(self.moved_list) < 20 else -20
        # Assemble and set the points
        self.moved_plot.points = [(i, num_moved) for i, num_moved in enumerate(self.moved_list[start_index:])]
        self.want_to_move_plot.points = [(i, num_want_moved) for i, num_want_moved in enumerate(self.want_to_move_list[start_index:])]

        self.want_mov_graph.xmax = len(self.want_to_move_list[start_index:]) + 1
        self.want_mov_graph.x_ticks_major = len(self.want_to_move_list[start_index:]) // 10
        self.want_mov_graph.x_ticks_minor = len(self.want_to_move_list[start_index:]) // 100
        self.want_mov_graph.ymax = max(self.want_to_move_list[start_index:]) + 10
        self.want_mov_graph.ymin = min(self.want_to_move_list[start_index:]) - 10

        self.mov_graph.xmax = len(self.moved_list[start_index:]) + 1
        self.mov_graph.x_ticks_major = len(self.moved_list[start_index:]) // 10
        self.mov_graph.x_ticks_minor = len(self.moved_list[start_index:]) // 100
        self.mov_graph.ymax = max(self.moved_list[start_index:]) + 10
        self.mov_graph.ymin = min(self.moved_list[start_index:])- 10

class TownWealthGraph(RelativeLayout):
    pop_graph = ObjectProperty(None)

    def __init__(self, town_colors: List[List[int]]):
        super().__init__()
        num_towns = len(town_colors)

        self.wealth_lists = [[] for _ in range(num_towns)]
        self.plots = [LinePlot(color=town_color, line_width=2) for town_color in town_colors]

        for plot in self.plots:
            self.wealth_graph.add_plot(plot)

    def update_graph(self):
        y_max = 0
        for i, plot in enumerate(self.plots):
            start_index = 0 # if len(self.population_lists[i]) < 100 else -100
            # Assemble and set the points
            plot.points = [(i, pop) for i, pop in enumerate(self.wealth_lists[i][start_index:])]
            y_max_temp = max(self.wealth_lists[i][start_index:])
            if y_max_temp > y_max:
                y_max = y_max_temp

        # Extend the plots max x
        self.wealth_graph.xmax = len(self.wealth_lists[0][start_index:]) + 1
        self.wealth_graph.x_ticks_major = self.wealth_graph.xmax // 10
        self.wealth_graph.x_ticks_minor = self.wealth_graph.xmax // 100

        self.wealth_graph.ymax = y_max
        self.wealth_graph.y_ticks_major = y_max // 10
        self.wealth_graph.y_ticks_minor = y_max // 100

class AverageWealthGraph(RelativeLayout):
    avg_wealth_graph = ObjectProperty(None)

    def __init__(self, town_colors: List[List[int]]):
        super().__init__()
        num_towns = len(town_colors)

        self.wealth_lists = [[] for _ in range(num_towns)]
        self.plots = [LinePlot(color=town_color, line_width=2) for town_color in town_colors]

        for plot in self.plots:
            self.avg_wealth_graph.add_plot(plot)

    def update_graph(self):
        y_max = 0
        for i, plot in enumerate(self.plots):
            start_index = 0 # if len(self.population_lists[i]) < 100 else -100
            # Assemble and set the points
            plot.points = [(i, pop) for i, pop in enumerate(self.wealth_lists[i][start_index:])]
            y_max_temp = max(self.wealth_lists[i][start_index:])
            if y_max_temp > y_max:
                y_max = y_max_temp

        # Extend the plots max x
        self.avg_wealth_graph.xmax = len(self.wealth_lists[0][start_index:]) + 1
        self.avg_wealth_graph.x_ticks_major = self.avg_wealth_graph.xmax // 10
        self.avg_wealth_graph.x_ticks_minor = self.avg_wealth_graph.xmax // 100

        self.avg_wealth_graph.ymax = y_max
        self.avg_wealth_graph.y_ticks_major = y_max // 10
        self.avg_wealth_graph.y_ticks_minor = y_max // 100

class MarketDemandGraph(RelativeLayout):
    market_dmd_graph = ObjectProperty(None)

    def __init__(self, town_colors: List[List[int]]):
        super().__init__()
        num_towns = len(town_colors)

        self.demand_lists = [[] for _ in range(num_towns)]
        self.plots = [LinePlot(color=town_color, line_width=2) for town_color in town_colors]

        for plot in self.plots:
            self.market_dmd_graph.add_plot(plot)

    def update_graph(self):
        y_max = 0
        
        for i, plot in enumerate(self.plots):
            start_index = 0 # if len(self.population_lists[i]) < 100 else -100
            # Assemble and set the points
            plot.points = [(i, pop) for i, pop in enumerate(self.demand_lists[i][start_index:])]
            y_max_temp = max(self.demand_lists[i][start_index:])
            if y_max_temp > y_max:
                y_max = y_max_temp

        # Extend the plots max x
        self.market_dmd_graph.xmax = len(self.demand_lists[0][start_index:]) + 1
        self.market_dmd_graph.x_ticks_major = self.market_dmd_graph.xmax // 10
        self.market_dmd_graph.x_ticks_minor = self.market_dmd_graph.xmax // 100

        self.market_dmd_graph.ymax = y_max
        self.market_dmd_graph.y_ticks_major = y_max // 10
        self.market_dmd_graph.y_ticks_minor = y_max // 100

class ControlPanel(BoxLayout):
    def __init__(self, start_callback, kwargs):
        super().__init__(**kwargs)
        self.start_callback = start_callback
        self.sim_started = False

    def start_stop_sim(self):
        self.sim_started = not self.sim_started

        if self.sim_started:
            self.ids.go_button.text = "Stop"
            Clock.schedule_interval(self.start_callback, 1/10)
        else:
            self.ids.go_button.text = "Go"
            
        

class PartyPlatformApp(App):
    go_button = Button()

    def __init__(self):
        super().__init__()
        self.world = World()
        self.update_graphs_dt = 0

    def step_sim(self, dt):
        step_info = self.world.step_world()
        self.update_graphs_dt += dt

        for town_index in range(len(self.world.towns)):
            self.population_graph.population_lists[town_index].append(len(self.world.towns[town_index].people))
            self.wealth_graph.wealth_lists[town_index].append(self.world.towns[town_index].get_total_wealth())

        self.movers_graph.moved_list.append(step_info.number_people_moved)
        self.movers_graph.want_to_move_list.append(step_info.number_people_desire_moved)

        for i, mc in enumerate(step_info.current_market.moving_costs):
            self.town_moving_cost_graph.demand_lists[i].append(mc)
        

        if self.control_panel.sim_started and self.update_graphs_dt > 0.5:
            self.population_graph.update_graph()
            self.movers_graph.update_graph()
            self.town_moving_cost_graph.update_graph()
            self.wealth_graph.update_graph()
            self.update_graphs_dt = 0
        else:
            return self.control_panel.sim_started
    
    @property
    def town_colors(self):
        if not hasattr(self, "_town_colors"):
            randint = random.randint
            self._town_colors = [[randint(0,100) / 100, randint(0,100) / 100, randint(0,100) / 100, 1] for _ in range(len(self.world.towns))]
        
        return self._town_colors
    
    def build(self):
        root_grid = GridLayout(rows=2 + len(self.world.towns))
        graph_grid = GridLayout(cols=2)

        self.population_graph = PopulationGraph(self.town_colors)
        self.wealth_graph = TownWealthGraph(self.town_colors)
        self.town_moving_cost_graph = MarketDemandGraph(self.town_colors)
        self.movers_graph = PeopleMovedGraph()
        self.control_panel = ControlPanel(self.step_sim, {"size_hint":(1, 0.3)})

        graph_grid.add_widget(self.population_graph)
        graph_grid.add_widget(self.movers_graph)
        graph_grid.add_widget(self.wealth_graph)
        graph_grid.add_widget(self.town_moving_cost_graph)
        root_grid.add_widget(graph_grid)

        root_grid.add_widget(self.control_panel)

        return root_grid

if __name__ == "__main__":
    PartyPlatformApp().run()