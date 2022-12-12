from observer import State_observer
from mob import Mob
from state_message import State_message
from mob import Mob_state


def m_round(num):
    num = int(num + (0.5 if num > 0 else -0.5))
    return num


class Field:
    def __init__(self, master, arr):
        self.plates = arr
        self.columns = len(arr[0])
        self.rows = len(arr)
        self.habitants = dict()
        self.master = master
        self.state_observer = State_observer(self)

    def are_coords_safe_to_move(self, x, y):
        #print("are these:", y, x)
        if self.plates[m_round(y)][m_round(x)] != "#":
            return True
        else:
            return False

    def is_anybody_there(self, x, y):
        for i in self.habitants.keys():
            if m_round(x) == m_round(self.habitants[i].get_x()) and m_round(y) == m_round(self.habitants[i].get_y()):
                return self.habitants[i]
        else:
            return None

    def update(self, lag):
        for i in self.habitants.keys():
            if isinstance(self.habitants[i], Mob):
                self.habitants[i].update(lag)

    def new_state(self, id, state):
        self.master.update_state_label(id, state)
        if state == Mob_state.STATE_FOUND:
            self.master.game_over(id, Mob_state.STATE_FOUND)
            self.habitants[id].state = Mob_state.STATE_PATROLLING
            self.master.game_over(id, Mob_state.STATE_PATROLLING)

    def add_habitant(self, habitant):
        if not habitant.get_id() in self.habitants:
            self.habitants[habitant.get_id()] = habitant
            if isinstance(habitant, Mob):
                self.state_observer.add_id(habitant.get_id())
                self.state_observer.do_work(State_message(habitant.id, type(habitant).__name__, habitant.state))
        else:
            pass
