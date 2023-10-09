#!/usr/bin/env python3

from dataclasses import dataclass
from functools import cached_property
import random
from typing import Dict, List
from vindonissa.game_objects.laws import CityLaws
from vindonissa.game_objects.title import CityTitle
from vindonissa.static_data.gamemetrics import POP_CONVERSION_MAX, FOOD_PRODUCTION_BASE, FOOD_PRODUCTION_MOD, MINING_PRODUCTION, TRADE_PRODUCTION, FORESTRY_PRODUCTION
from vindonissa.game_objects.pop import Work

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from vindonissa.game_objects.cell import Cell
    from vindonissa.game_objects.culture import Culture
    from vindonissa.game_objects.pop import Pop


class WayNode(object):
    """
    Acts as parent class for cities and ports.
    """
    def __init__(self, cell):
        self.cell: Cell = cell

        self.neighbors: List[City] = []  # holds all neighboring cities
        self.land_connections: Dict[int, int] = {}  # keeps track of path cost
        self.sea_connections: Dict[int, int] = {}

        # util attributes
        self.distance = 0
        self.search_heuristic = 0
        self.path_from: WayNode|None = None
        self.next_cell_with_same_prio: WayNode|None = None

    @property
    def search_priority(self) -> int:
        return self.distance + self.search_heuristic
    
    def get_distance(self, other) -> int:
        if type(self) == City:
            if type(other) == Port:
                return 40
            else:
                return self.land_connections[other.id]
        elif type(self) == Port:
            if type(other) == City:
                return 40
            else:
                for p, v in self.port_connections:
                    if p == other:
                        return v
        return 999  # should never be reached
    
@dataclass
class Capacity(object):
    work_type: Work|None = None

    maximum: float = 0
    worked: int = 0

    base_production: float = 0  # what a single worker produces
    production: float = 0  # what is produced in total atm
    
    @property
    def expected_production(self) -> float:
        return self.production + self.base_production
    
    @property
    def red_expected_production(self) -> float:
        return self.production - self.base_production

    @property
    def is_overextended(self) -> bool:
        return self.worked > self.maximum
    
    @property
    def would_be_overextended(self) -> bool:
        return self.worked + 1 > self.maximum
    
    @property
    def red_would_be_overextended(self) -> bool:
        return self.worked - 1 > self.maximum
    

class Capacities(object):
    def __init__(self, city: "City"):
        self.city = city

        self.farming = Capacity(Work.Farming)
        self.fishing = Capacity(Work.Fishing)
        self.mining = Capacity(Work.Mining)
        self.forestry = Capacity(Work.Forestry)
        self.trade = Capacity(Work.Trade)

        self.capacities = [self.farming, self.fishing, self.mining, self.forestry, self.trade]

    @property
    def food_maximum(self):
        return self.farming.maximum + self.fishing.maximum
    
    @property
    def food_production(self):
        return self.farming.production + self.fishing.production
    
    @property
    def wealth_production(self):
        return self.mining.production + self.forestry.production + self.trade.production

    def get_exp_value_when_raised(self, cap: Capacity) -> float:
        """
        Returns the expected priority of the capacity if one worker would be added.
        """
        val = cap.base_production

        if cap.would_be_overextended:
            val *= 0.5

        if cap == self.farming or cap == self.fishing:
            expected_production = self.food_production + val
            if expected_production > (self.city.pop_size + 10):
                val *= 0.5
            else:
                val *= 2

        return val
    
    def get_curr_value(self, cap: Capacity) -> float:
        """
        Returns the expected priority of the capacity if one worker would be added.
        """
        val = cap.base_production

        if cap.is_overextended:
            val *= 0.5

        if cap == self.farming or cap == self.fishing:
            if self.food_production > (self.city.pop_size + 10):
                val *= 0.5
            else:
                val *= 2

        return val
    
    def raise_capacity(self, cap: Capacity, value: float):
        """
        Raise the maximum of a capacity and change the values accordingly.
        """
        cap.maximum += value
        if cap.is_overextended:
            cap.production = (cap.maximum * cap.base_production) + ((cap.worked - cap.maximum) * cap.base_production * 0.5)
        else:
            cap.production = cap.worked * cap.base_production

    def lower_capacity(self, cap: Capacity, value: float):
        """
        Lowers the capacity maximum, modifies values where needed.
        """
        cap.maximum -= value
        if cap.is_overextended:
            cap.production = (cap.maximum * cap.base_production) + ((cap.worked - cap.maximum) * cap.base_production * 0.5)
        else:
            cap.production = cap.worked * cap.base_production

    def remove_worker(self, cap: Capacity):
        """
        Remove a worker from a capacity and checks if the capacitys value needs to be modified.
        """
        if cap.is_overextended:
            cap.production -= cap.base_production * 0.5
        else:
            cap.production -= cap.base_production
        cap.worked -= 1
    
    def add_worker(self, cap: Capacity):
        """
        Adds a worker to a capacity and checks if the capacitys value needs to be modified.
        """
        cap.worked += 1
        if cap.is_overextended:
            cap.production += cap.base_production * 0.5
        else:
            cap.production += cap.base_production
    
    def set_initial_values(self, city):
        self.farming.base_production = FOOD_PRODUCTION_BASE + FOOD_PRODUCTION_MOD * city.fertility * 2
        self.fishing.base_production = FOOD_PRODUCTION_BASE + FOOD_PRODUCTION_MOD * city.fertility * 2
        self.mining.base_production = MINING_PRODUCTION  # modify by ore quality?
        self.forestry.base_production = FORESTRY_PRODUCTION  # modify by something?
        self.trade.base_production = TRADE_PRODUCTION


class City(WayNode):
    def __init__(self, id: int, cell):
        super().__init__(cell)
        self.id = id
        
        self.terrain: List[Cell] = []

        cell.city_center = self
        cell.city = self
        self.terrain.append(cell)
        for c in cell.neighbors:
            c.city = self
            self.terrain.append(c)

        # capacities & pops
        self.capacities = Capacities(self)
        self.pops: List[Pop] = []

        # ports and distances to ports
        self.ports: List[Port] = []
        self.port_connections: List[int] = []

        # culture and religion
        self.culture: Culture|None = None
        self.laws = CityLaws()

        # title and ownership
        self.title = CityTitle(self.id, self, self.laws)

    @property
    def wealth(self):
        food_diff = self.capacities.food_production - self.pop_size
        if food_diff >= 0:
            # enough food, surplus food is converted into wealth at a 2:1 rate
            return food_diff * 0.5 + self.capacities.wealth_production
        else:
            return self.capacities.wealth_production + food_diff * 2 

    @cached_property
    def fertility(self):
        """
        Cached because this value shouldn't change over time.
        """
        return sum([f.fertility for f in self.terrain]) / len(self.terrain)

    @property
    def pop_size(self):
        return sum([p.size for p in self.pops])
    
    def set_inital_values(self):
        self.capacities.set_initial_values(self)  # TODO: Move to be only executed once, not every year
        self.update_pop_assignments(disable_cap=True)
        self.update_production()
    
    def yearly_updates(self):
        """
        Do yearly updates for the city such as population growth,
        pop assignment etc.
        """
        self.update_pop_assignments()
        self.update_production()
    
    def update_pop_assignments(self, disable_cap = False):
        """
        Update which capacities are worked by pops.

        For the moment, we only allocate new pops, later we need to do reallocation as well.
        """
        pop_conversion_pool = POP_CONVERSION_MAX * self.pop_size
        if disable_cap:
            pop_conversion_pool = 1000

        unassigned_pops = [pop for pop in self.pops if pop.work == Work.Unassigned]

        converted = 0
        while unassigned_pops and converted < pop_conversion_pool:
            curr_pop = unassigned_pops[0]
            # get the highest prio capacity
            sorted_caps = sorted(self.capacities.capacities, key=lambda x: (self.capacities.get_exp_value_when_raised(x), -(x.worked/max(x.maximum, 1))), reverse=True)
            highest_prio_cap = sorted_caps[0]

            # Add worker
            self.capacities.add_worker(highest_prio_cap)

            # Create new pop if necessary or add to a fitting pop
            new_pop = curr_pop.split_off_for_work(highest_prio_cap.work_type)  # type: ignore
            po = None
            for p in self.pops:
                if p.check_if_equal_but_not_same(new_pop):
                    po = p
                    break
            if po is not None:
                new_pop = po
            else:
                self.pops.append(new_pop)

            # size + 1 new pop
            new_pop.size += 1

            # Downsize old pop
            curr_pop.size -= 1
            if curr_pop.size == 0:
                self.pops.remove(curr_pop)
                unassigned_pops.remove(curr_pop)
                del curr_pop

            converted += 1

        while converted < pop_conversion_pool:
            add_exp_cap_values = sorted(self.capacities.capacities, key=lambda x: (self.capacities.get_exp_value_when_raised(x), -(x.worked/max(x.maximum, 1))), reverse=True)
            red_exp_cap_values = sorted([c for c in self.capacities.capacities if c.worked > 0], key=lambda x: (self.capacities.get_curr_value(x), -(x.worked/max(x.maximum, 1))), reverse=True)

            highest_prio_cap_to_raise = add_exp_cap_values[0]
            highest_prio_cap_to_lower = red_exp_cap_values[-1]

            if self.capacities.get_exp_value_when_raised(highest_prio_cap_to_raise) > self.capacities.get_curr_value(highest_prio_cap_to_lower):
                self.capacities.add_worker(highest_prio_cap_to_raise)
                
                # look for a pop to downsize (maybe weight this by pop size?)
                curr_pop = random.choice([pop for pop in self.pops if pop.work == highest_prio_cap_to_lower.work_type])
                # modify pop sizes, create new pops if necessary
                new_pop = curr_pop.split_off_for_work(highest_prio_cap.work_type)  # type: ignore
                po = None
                for p in self.pops:
                    if p.check_if_equal_but_not_same(new_pop):
                        po = p
                        break
                if po is not None:
                    new_pop = po
                else:
                    self.pops.append(new_pop)

                # size + 1 new pop
                new_pop.size += 1

                self.capacities.remove_worker(highest_prio_cap_to_lower)
                # modify pop sizes, create new pops if necessary
                
                # Downsize old pop
                curr_pop.size -= 1
                if curr_pop.size == 0:
                    self.pops.remove(curr_pop)
                    unassigned_pops.remove(curr_pop)
                    del curr_pop

                converted += 1
            else:
                break

    def update_production(self):
        """
        Calculate the new wealth of the city.
        """
        pass


class Port(WayNode):
    def __init__(self, id: int, city: City, cell):
        super().__init__(cell)
        self.id = id
        self.city = city

        self.port_connections: List[tuple[Port, int]] = []
        
