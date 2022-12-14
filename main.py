import time
import tkinter as tk

from point import Point
from mob import Mob
from canvas import canvas
from field import Field
from player import Player, Player_state
from path_node import Node, Route

PHYSICS_FPS = 60
MS_PER_UPDATE = 1 / PHYSICS_FPS


class Window(tk.Tk):

    def __init__(self):

        super().__init__()

        self.work_status = True
        self.tile_size = 55
        self.half_tile_size = self.tile_size // 2
        self.third_tile_size = self.tile_size // 3

        self.protocol("WM_DELETE_WINDOW", self.finish)
        self.title('RIM')

        self.label_bg = tk.Label(master=self)
        self.label_bg.grid(column = 0, row = 0, columnspan = 2)
        self.lag = 0
        self.cummulative_lag = 0 #  used for player because of architecture

        self.state_labels = []
        self.label_id1 = tk.Label(master=self, text = "NPC1: Blue")
        self.label_id2 = tk.Label(master=self, text = "NPC2: Green")

        self.label_id1.grid(column=0, row=1)
        self.label_id2.grid(column=1, row=1)

        for i in range(2):
            self.state_labels.append(tk.Label(master=self))
            self.state_labels[i].grid(column=i, row=2)


        self.bind("<KeyRelease>", self.process_input)
        self.bind("<KeyPress>", self.process_input)

        self.lag = 0
        #####
        lvl = open("lvl.txt", 'r')
        y = int(lvl.readline().strip())
        lvl_structure = []
        for i in range(y):
            lvl_structure.append(list(lvl.readline().strip()))

        x = len(lvl_structure[0])
        self.field = Field(self, lvl_structure)

        self.H = y * self.tile_size
        self.W = x * self.tile_size
        self.geometry(str(self.W) + 'x' + str(self.H + 50))
        self.canvas = canvas(self.W + 1, self.H + 1)

        nodes_1 = [Node(7, 3, self.tile_size),  Node(7, 9, self.tile_size) , Node(14, 6, self.tile_size)]
        nodes_2 = [Node(1, 6, self.tile_size), Node(18, 3, self.tile_size), Node(18, 10, self.tile_size), ]
        self.field.add_habitant(Mob(1, self.field, 7, 3, (0, 0, 255), Route(nodes_1)))
        self.field.add_habitant(Mob(2, self.field, 1, 6, (0, 255, 0), Route(nodes_2)))

        self.player = Player(3, self.field, 18, 1, (255, 0, 0))
        self.field.add_habitant(self.player)

    def update_state_label(self, id, state):
        self.state_labels[id - 1].configure(text=state.name)

    def start(self):
        prev_t = time.time()
        start_time = time.time()
        phys_frame_counter = 0
        graphic_frame_counter = 0

        while self.work_status:
            curr_t = time.time()
            elapsed = curr_t - prev_t

            prev_t = curr_t
            self.lag += elapsed
            self.cummulative_lag = self.lag
            #print(self.lag)
            while self.lag >= MS_PER_UPDATE:
                phys_frame_counter += 1
                self.field.update(MS_PER_UPDATE)
                self.lag -= MS_PER_UPDATE
            graphic_frame_counter += 1

            self.render()
            self.tkinter_update()

        end_time = time.time()
        print(" Physic_fps:", phys_frame_counter / (end_time - start_time), "\n",
              " Graphic_fps: ", graphic_frame_counter / (end_time - start_time), "\n",
              " Global_time:", (end_time - start_time), "\n"
              )

    def process_input(self, event):

        if event.type == '2':     #press
            self.player.state = Player_state.STATE_MOVING
            self.player.angle = self.player.angle_table[event.keysym]
            self.player.update(MS_PER_UPDATE)

        elif event.type == 3:   #relesae
            self.player.state = Player_state.STATE_STATIONARY
        else:
            pass

    def render(self):
        self.canvas.clear()

        self.draw_habitants()

        self.draw_blocks()
        self.draw_grid()
        self.set_image()

    def draw_grid(self):
        for i in range(self.field.rows):
            self.canvas.draw_line(
                Point(0, i * self.tile_size),
                Point(self.W, i * self.tile_size),
                (0, 0, 0)
            )
        for i in range(self.field.columns):
            self.canvas.draw_line(
                Point(i * self.tile_size, 0),
                Point(i * self.tile_size, self.H),
                (0, 0, 0)
            )

    def draw_blocks(self):
        for i in range(self.field.rows):
            for j in range(self.field.columns):
                if self.field.plates[i][j] == "#":
                    self.canvas.draw_filled_squre(
                        Point(j * self.tile_size, i * self.tile_size),
                        Point(j * self.tile_size + self.tile_size, i * self.tile_size + self.tile_size),
                        (255, 255, 0)
                    )

    def draw_fov(self, mob):
        s = Point(mob.x * self.tile_size + self.half_tile_size, mob.y * self.tile_size + self.half_tile_size)
        for i in mob.endpoints:
            self.canvas.draw_line(
                s,
                Point(i[0] * self.tile_size + self.half_tile_size, i[1] * self.tile_size + self.half_tile_size),
                mob.color
            )

    def draw_habitants(self):
        for i in self.field.habitants.keys():
            if isinstance(self.field.habitants[i], Mob):
                self.draw_fov(self.field.habitants[i])

        for i in self.field.habitants.keys():
            x, y = self.field.habitants[i].x * self.tile_size, self.field.habitants[i].y * self.tile_size
            a = Point(x, y)
            b = Point(x + self.tile_size, y + self.tile_size)

            self.canvas.draw_filled_squre(a, b, self.field.habitants[i].color)

            if not isinstance(self.field.habitants[i], Player):

                if self.field.habitants[i].get_route() is not None:
                    for node in self.field.habitants[i].get_route().get_nodes():

                        x, y = node.x * self.tile_size + self.third_tile_size, node.y * self.tile_size + self.third_tile_size
                        a = Point(x, y)
                        b = Point(x + self.third_tile_size , y + self.third_tile_size)
                        self.canvas.draw_filled_squre(a, b, self.field.habitants[i].color)

                    # start ------------------- end  then end becomes new start
                    start = self.field.habitants[i].get_route().get_nodes()[0]
                    for end in self.field.habitants[i].get_route().get_nodes()[0:]:
                        a = Point(start.field_x, start.field_y)
                        b = Point(end.field_x, end.field_y)
                        self.canvas.draw_line(a, b, self.field.habitants[i].color)
                        start = end

                    a = Point(end.field_x, end.field_y)
                    b = Point(
                        self.field.habitants[i].get_route().get_nodes()[0].field_x,
                              self.field.habitants[i].get_route().get_nodes()[0].field_y
                              )
                    self.canvas.draw_line(a, b, self.field.habitants[i].color)

    def tkinter_update(self):
        self.update()
        self.update_idletasks()

    def set_image(self):
        stg_img = self.canvas.get_image_for_tk()
        self.label_bg.configure(image=stg_img)
        self.label_bg.image = stg_img

    def finish(self):
        self.work_status = False

    def game_over(self, id, state):
        self.update_state_label(id, state)
        self.tkinter_update()
        time.sleep(1)
        self.lag -= 1
        self.player.set_x(18)
        self.player.set_y(1)



res = Window()
res.start()
