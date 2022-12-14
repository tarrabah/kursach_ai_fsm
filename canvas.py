from PIL import Image, ImageDraw
import PIL.ImageTk
from point import Point


def m_round(num):
    num = int(num + (0.5 if num > 0 else -0.5))
    return num


class canvas:
    def __init__(self, C_w, C_h):
        self.C_w = C_w
        self.C_h = C_h
        self.image = Image.new('RGB', (C_w, C_h), 'white')
        self.drawer = ImageDraw.Draw(self.image)
        self.pixels = self.image.load()

        self.boundary_check_x = self.C_w - 1
        self.boundary_check_y = self.C_h - 1

        self.num = 1

    def set_pixel(self, x, y, color_tuple):  # x - [-Cw / 2; Cw/2], y - [-Ch/2; Ch/2]
        x = round(x)
        y = round(y)

        if abs(x) > self.boundary_check_x or abs(y) > self.boundary_check_y:
            return

        self.pixels[x, y] = color_tuple

    def set_int_pixel(self, x, y, color_tuple):  # x - [-Cw / 2; Cw/2], y - [-Ch/2; Ch/2]

        if abs(x) > self.boundary_check_x or abs(y) > self.boundary_check_y:
            return

        if abs(x) > self.boundary_check_x or abs(y) > self.boundary_check_y:
            return

        self.pixels[x, y] = color_tuple

    def clear(self):
        self.drawer.rectangle((0, 0, self.C_w, self.C_h), fill="white")

    def save(self):
        self.image.save('frame__%d.png' % self.num)
        self.num += 1

    '''
    рисует линию в координатах холста
    т.е. рисуется отрезок между пикселями
    а координаты мира смасшабированы относительно размеров экрана
    (c поправкой, на то, что центр (0, 0) перенесён в центр холста и ось y смотрит вверх)
    '''

    def draw_line(self, p1, p2, color):
        self.drawer.line((p1.x, p1.y, p2.x, p2.y), fill=color, width=1)

    '''
        if p1.x == p2.x and p1.y == p2.y:
            return

        dx = p2.x - p1.x
        dy = p2.y - p1.y

        if abs(dx) > abs(dy):
            # Прямая ближе к горизонтальной
            if p1.x > p2.x:
                p1, p2 = p2, p1

            dy_dx = dy / dx
            y = p1.y

            for x in range(m_round(p1.x), m_round(p2.x + 1)):
                rounded_y = m_round(y)
                self.set_int_pixel(x, rounded_y, color)
                y += dy_dx
        else:
            # Прямая ближе к вертикальной
            if p1.y > p2.y:
                p1, p2 = p2, p1

            dy_dx = dx / dy
            x = p1.x
            for y in range(m_round(p1.y), m_round(p2.y + 1)):
                rounded_x = m_round(x)
                self.set_int_pixel(rounded_x, y, color)
                x += dy_dx
        '''

    def draw_traingle_frame(self, A, B, C, color):
        if B.y < A.y:
            A, B = B, A
        if C.y < A.y:
            C, A = A, C
        if C.y < B.y:
            C, B = B, C

        self.draw_line(A, B, color)
        self.draw_line(B, C, color)
        self.draw_line(A, C, color)

    def draw_filled_traingle(self, T, color, m=1):
        # print(11)
        A = T.P1 * m
        B = T.P2 * m
        C = T.P3 * m

        if B.y < A.y:
            A, B = B, A
        if C.y < A.y:
            C, A = A, C
        if C.y < B.y:
            C, B = B, C

        self.draw_line(A, B, color)
        self.draw_line(B, C, color)
        self.draw_line(A, C, color)

        """
             A
           /\
          /  \     top segment
         /____\
        B\     \
           \    \
             \   \
               \  \  bottom segment
                 \ \
                   \
                    C
        """

        total_height = C.y - A.y + 1
        segment_height = B.y - A.y + 1

        dx_C_A = C.x - A.x
        dx_B_A = B.x - A.x

        for y in range(m_round(A.y), m_round(B.y)):
            progress = y - A.y
            alpha = progress / total_height
            beta = progress / segment_height
            a = Point(A.x + dx_C_A * alpha, y)
            b = Point(A.x + dx_B_A * beta, y)

            self.draw_line(a, b, color)

        dx_C_B = C.x - B.x

        segment_height = C.y - B.y + 1
        for y in range(m_round(B.y), m_round(C.y)):
            progress = y - A.y
            alpha = progress / total_height
            beta = (y - B.y) / segment_height
            a = Point(A.x + dx_C_A * alpha, y)
            b = Point(B.x + dx_C_B * beta, y)

            self.draw_line(a, b, color)

    def get_image_for_tk(self):
        return PIL.ImageTk.PhotoImage(self.image)

    def draw_filled_squre(self, P1, P2, color):
        '''
        p1 left top
        p2 right bot
        '''
        if P1.x < P2.x:
            x_start = P1.x
            x_end = P2.x
        else:
            x_start = P2.x
            x_end = P1.x

        if P1.y < P2.y:
            y_start = P1.y
            y_end = P2.y
        else:
            y_start = P2.y
            y_end = P1.y

        for y in range(m_round(y_start), m_round(y_end)):
            self.draw_line(
                Point(x_start, y),
                Point(x_end, y),
                color
            )
