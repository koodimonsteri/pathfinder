from pygame import Rect

class GridCamera:
    def __init__(self, x, y, w_size):
        self.x = x
        self.y = y
        self.width = w_size
        self.height = w_size
        self.current_scale = 1
        self.dragging = False
        self.drag_x = 0
        self.drag_y = 0

    def zoom(self, mx, my, zoom_in):
        if self.in_bounds(mx, my):
            old_s = self.current_scale
            tx0, ty0 = self.scrtogrid(mx, my)
            s = self.current_scale + (1 if zoom_in else - 1)
            s = max(1, min(16, s))
            if old_s != s:
                self.current_scale = s
                tx1, ty1 = self.gridtoscr(tx0, ty0)
                self.x += mx - tx1
                self.y += (my - ty1)
            
            
    def drag(self, mx, my, dx, dy):
        pass

    def apply_drag(self):
        pass

    # Update drag variables
    def update_drag(self, mx, my, dx, dy):
        self.drag_x = dx
        self.drag_y = dy
    
    def scrtogrid(self, mx, my):
        nx = int((mx - self.x) / self.current_scale)
        ny = int((my - self.y) / self.current_scale)
        return (nx, ny)

    def gridtoscr(self, mx, my):
        nx = int(self.x + (mx * self.current_scale))
        ny = int(self.y + (my * self.current_scale))
        return (nx, ny)

    def screen_to_grid(self, mx, my):
        nx = int((mx / self.current_scale) - self.x)
        ny = int((my / self.current_scale) - self.y)
        return (nx, ny)
    
    def grid_to_screen(self, cx, cy):
        nx = int((self.x + cx) * self.current_scale)
        ny = int((self.y + cy) * self.current_scale)
        return (nx, ny)

    def in_bounds(self, m_x, m_y):
        return m_x >= 0 and m_x < self.width and m_y >= 0 and m_y < self.height

    def get_camera_rect(self):
        rect = Rect(self.x, self.y, self.width, self.height)
