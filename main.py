import time
import tkinter as tk

from point import Point
from mob import Mob
from canvas import canvas
from field import Field
from player import Player, Player_state
from path_node import Node, Route
from tkinter import messagebox

PHYSICS_FPS = 60
MS_PER_UPDATE = 1 / PHYSICS_FPS


class Window(tk.Tk):

    def __init__(self):

        super().__init__()

        self.work_status = True
        self.tile_size = 35
        self.half_tile_size = self.tile_size // 2
        self.third_tile_size = self.tile_size // 3

        self.protocol("WM_DELETE_WINDOW", self.finish)
        self.title('RIM')

        self.label_bg = tk.Label(master=self)

        self.lag = 0
        self.cumulative_lag = 0

        self.score = 0
        self.lives = 2
        self.max_score = 2560

        self.state_labels = []
        self.label_id1 = tk.Label(master=self, text = "NPC1: Blue")
        self.label_id2 = tk.Label(master=self, text = "NPC2: Green")
        self.label_score = tk.Label(master=self, text = "SCORE: 0")
        self.label_lives = tk.Label(master=self, text="Lives: " + str(self.lives))

        self.label_id1.grid(column=0, row=2)
        self.label_id2.grid(column=1, row=2)
        self.label_score.grid(column=0, row=0)
        self.label_lives.grid(column=1, row=0)
        self.label_bg.grid(column=0, row=1, columnspan=2)

        for i in range(2):
            self.state_labels.append(tk.Label(master=self))
            self.state_labels[i].grid(column=i, row=3)

        self.bind("<KeyRelease>", self.process_input)
        self.bind("<KeyPress>", self.process_input)

        self.lag = 0
        #####
        lvl_structure, width, height, teleports, routes = self.load_level("lvl.txt")

        self.H = height * self.tile_size
        self.W = width * self.tile_size

        self.field = Field(self, lvl_structure, height, width, teleports)
        self.geometry(str(self.W) + 'x' + str(self.H + 50))
        self.canvas = canvas(self.W + 1, self.H + 1)

        self.player = Player(0, self.field, 1, 1, (255, 0, 0))
        self.field.add_habitant(self.player)
        id = 1
        for i in routes:
            self.field.add_habitant(Mob(id, self.field, *i[0].get_x_y(), (0, 155, 255), Route(i)))
            id += 1

    def load_level(self, filename):
        lvl = open(filename, 'r')
        lvl_data = list(map(lambda x: x.strip(), lvl.readlines()))
        index = 0
        lvl_structure = []
        ## load level structure
        while True:
            index += 1
            if lvl_data[index] != "level start":
                break

        while lvl_data[index] != "level end":
            lvl_structure.append(list(lvl_data[index]))
            index += 1

        while True:
            index += 1
            if lvl_data[index] != "level end":
                break

        ## load teleports
        teleports = []
        while True:
            index += 1
            if lvl_data[index] != "teleports start":
                break

        while lvl_data[index] != "teleports end":
            teleports.append(list(map(lambda x: list(map(int, x.split(' '))),lvl_data[index].split('-'))))
            index += 1

        while True:
            index += 1
            if lvl_data[index] != "teleports end":
                break

        ## load nodes and creatures
        creatures = []
        paths = []
        j = -1
        index += 1
        while lvl_data[index] != "mobs end":

            if lvl_data[index] != "mob start":
                break
            index += 1

            paths.append([])
            j += 1
            while lvl_data[index] != "mob end":
                x, y = list(map(int, lvl_data[index].split(' ')))
                paths[j].append(Node(x, y, self.tile_size))
                index += 1
            index += 1

        #print(lvl_data[index], sep='\n')

        width = len(lvl_structure)
        height = len(lvl_structure[0])

        return lvl_structure, height, width, teleports, paths

    def increase_score(self, val):
        self.score += val
        self.label_score.configure(text = "SCORE: "+str(self.score))


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
            self.cumulative_lag = self.lag
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
            prev_angle = self.player.angle
            self.player.state = Player_state.STATE_MOVING
            self.player.angle = self.player.angle_table[event.keysym]
            if event.keysym == "w" or event.keysym == "s":
                self.player.x = round(self.player.x)
            else:
                self.player.y = round(self.player.y)
            x, y = self.player.new_coords(0.5)

            if not self.player.can_move(x, y):
                self.player.angle = prev_angle

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
                        (0, 0, 0)
                    )
                elif self.field.plates[i][j] == "0":
                    self.canvas.draw_filled_squre(
                        Point(j * self.tile_size, i * self.tile_size),
                        Point(j * self.tile_size + self.tile_size, i * self.tile_size + self.tile_size),
                        (14, 250, 100)
                    )
                elif self.field.plates[i][j] == ".":
                    x, y = j * self.tile_size + self.third_tile_size, i * self.tile_size + self.third_tile_size
                    a = Point(x, y)
                    b = Point(x + self.third_tile_size, y + self.third_tile_size)
                    self.canvas.draw_filled_squre(a, b, (150, 150,0))

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
            '''
            if not isinstance(self.field.habitants[i], Player):

                if self.field.habitants[i].get_route() is not None:

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
            '''
    def tkinter_update(self):
        self.update()
        self.update_idletasks()

    def set_image(self):
        stg_img = self.canvas.get_image_for_tk()
        self.label_bg.configure(image=stg_img)
        self.label_bg.image = stg_img

    def finish(self):
        self.work_status = False

    def spotted(self, id, state):
        print("main.py, spotted - 1 life")
        self.update_state_label(id, state)

        time.sleep(1)
        self.lives -= 1
        if self.lives == -1:
            messagebox.showwarning("GAME OVER!", "NO MORE LIVES LEFT,\nYOUR SCORE: " + str(self.score))
            self.finish()

        self.label_lives.configure(text = "LIVES: " + str(self.lives))
        self.lag -= 1
        self.player.set_x(1)
        self.player.set_y(1)

    def win(self):
        messagebox.showwarning("YOU WON!", "CONGRATULATIONS!")
        self.finish()


res = Window()
res.start()
