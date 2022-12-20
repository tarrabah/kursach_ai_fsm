import math

class Node:
    def __init__(self, x, y, tile_size):
        self.x = x
        self.y = y
        self.tile_size = tile_size

        self.field_x = self.x * self.tile_size + self.tile_size // 2
        self.field_y = self.y * self.tile_size + self.tile_size // 2

    def dist_to(self, x, y):
        return math.sqrt((x - self.x) ** 2 + (y - self.y) ** 2)

    def angle_to(self, x, y):
        return math.atan2 ((self.y - y), (self.x - x))

    def __str__(self):
        return "x: " + str(self.x) + " y: " + str(self.y)

    def get_x_y(self):
        return (self.x, self.y)


class Route:
    def __init__(self, nodes):
        self.nodes = nodes
        self.len = len(nodes)

    def get_next_node_index(self, index):
        return (index + 1) % self.len

    def get_node_by_index(self, index):
        if index >= self.len:
            return self.nodes[0]
        else:
            return self.nodes[index]

    def get_nodes(self):
        return self.nodes

