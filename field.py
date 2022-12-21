from observer import State_observer
from mob import Mob
from state_message import State_message
from mob import Mob_state
from player import Player


def m_round(num):
    return round(num)


class Field:
    def __init__(self, master, arr, h, w, teleports = None):
        self.h = h
        self.w = w
        #print(self.h, self.w)
        self.plates = arr
        self.columns = len(arr[0])
        self.rows = len(arr)
        self.habitants = dict()
        self.master = master
        self.state_observer = State_observer(self)
        self.teleports = teleports

    def are_coords_safe_to_move(self, x, y):
        round_x = m_round(x)
        round_y = m_round(y)
        #print(round_x, round_y)
        if round_x > self.w - 1 or round_y > self.h - 1:
            return False

        if self.plates[round_y][round_x] == "#":
            return False
        else:
            return True

    def is_anybody_there(self, x, y):
        for i in self.habitants.keys():
            if m_round(x) == m_round(self.habitants[i].get_x()) and m_round(y) == m_round(self.habitants[i].get_y()):
                return self.habitants[i]
        else:
            return None

    def update(self, lag):
        for i in self.habitants.keys():
            x = m_round(self.habitants[i].get_x())
            y = m_round(self.habitants[i].get_y())
            if self.check_teleport(x, y):
                for j in self.teleports:
                    if j[0][0] == x and j[0][1] == y:
                        self.habitants[i].set_x(j[1][0])
                        self.habitants[i].set_y(j[1][1])
            if isinstance(self.habitants[i], Player):
                if self.plates[y][x] == '.':
                    #sprint("taken")
                    self.plates[y][x] = ' '
                    self.master.increase_score(10)
                    if self.master.score == self.master.max_score:
                        self.master.win()
            self.habitants[i].update(lag)

    def new_state(self, id, state):
        self.master.update_state_label(id, state)

    def on_spotting(self, id, s):
        if s == Mob_state.STATE_FOUND_DURING_PATROL:
            self.master.spotted(id, Mob_state.STATE_FOUND_DURING_PATROL)
            self.habitants[id].state = Mob_state.STATE_PATROL
        elif s == Mob_state.STATE_FOUND_WHILE_LOOKING_AROUND:
            self.master.spotted(id, Mob_state.STATE_FOUND_WHILE_LOOKING_AROUND)
            self.habitants[id].state = Mob_state.STATE_RETURN

    def add_habitant(self, habitant):
        if not habitant.get_id() in self.habitants:
            self.habitants[habitant.get_id()] = habitant
            if isinstance(habitant, Mob):
                self.state_observer.add_id(habitant.get_id())
                self.state_observer.do_work(State_message(habitant.id, type(habitant).__name__, habitant.state))
        else:
            pass

    def check_teleport(self, x, y):
        if self.teleports is None:
            return False
        else:
            if self.plates[y][x] == "0":
                return True
            else:
                return False
