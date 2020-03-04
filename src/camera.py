

class GridCamera:
    def __init__(self, x, y, w_size):
        self.x = x
        self.y = y
        self.size = w_size
        self.width = w_size
        self.height = w_size
        self.current_zoom = 1.0
        self.zoom_f = 0.1

    def zoom(self, mx, my, zoom_in):
        if self.in_bounds(mx, my):
            z = self.zoom_f if zoom_in else -self.zoom_f
            self.current_zoom += z
            tx = self.x + (mx / 2)
            ty = self.y + (my / 2)
            self.x -= mx * z
            self.y -= mx * z
            self.width = self.size * (1-z)
            self.height = self.size * (1-z)
    
    def drag(self, mx, my, d):
        pass
    
    def get_grid_coords(self, mx, my):
        pass

    def in_bounds(self, m_x, m_y):
        return m_x >= 0 and m_x < self.width and m_y >= 0 and m_y < self.height