from pygame import Rect

class GridCamera:
    def __init__(self, x, y, w_size):
        self.x = x
        self.y = y
        self.size = w_size
        self.width = w_size
        self.height = w_size
        self.current_zoom = 1.0
        self.zoom_f = 0.9
        self.dragging = False
        self.c_drag = Drag()
        self.current_scale = 1

    def zoom(self, mx, my, zoom_in):
        if self.in_bounds(mx, my):
            ts = int(self.current_scale + (1 if zoom_in else -1))
            ts = max(1, min(10, ts))
            self.current_scale = ts
            '''z = self.zoom_f if zoom_in else -self.zoom_f
            self.current_zoom += z
            tx = self.x + (mx / 2)
            ty = self.y + (my / 2)
            self.x -= mx * z
            self.y -= mx * z
            self.width = self.size * (1-z)
            self.height = self.size * (1-z)'''
    
    
    def drag(self, mx, my, d):
        pass
    
    def get_grid_coords(self, mx, my):
        pass

    def in_bounds(self, m_x, m_y):
        return m_x >= 0 and m_x < self.width and m_y >= 0 and m_y < self.height

    def get_camera_rect(self):
        rect = Rect(self.x, self.y, self.width, self.height)


class Drag:
    def __init__(self):
        self.mx = 0.0
        self.my = 0.0
        self.dx = 0.0
        self.dy = 0.0

    def update_drag(self, mx, my, dx, dy):
        if mx != self.mx and my != self.my:
            self.mx = mx
            self.my = my
            self.dx = dx
            self.dy = dy
        else:
            self.mx = mx
            self.my = my
            self.dx = 0.0
            self.dy = 0.0
    
    def __repr__(self):
        return "Drag, mouse pos (%f, %f) rel (%f, %f)" % (self.mx, self.my, self.dx, self.dy)
