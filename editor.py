import pygame, sys
from pygame.math import Vector2 as Vector
from pygame.mouse import get_pos as mouse_position
from pygame.image import load
from settings import *
from menu import Menu


class Editor:
    def __init__(self, tiles_data):
        # Window setup
        self.last_selected_cell = None
        self.display_surface = pygame.display.get_surface()

        # Navigation
        self.origin = Vector()  # origin point of the current window
        self.mouse_clicked = False
        self.offset = Vector(0, 0)  # Movement value in the 2D space

        # Support grid
        self.support_grid_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.support_grid_surface.set_colorkey("green")
        self.support_grid_surface.set_alpha(30)

        # Cursor
        cursor_surf = load("resources/cursors/cursor.png").convert_alpha()
        new_cursor_size = (28.35, 42.3)
        cursor_surf = pygame.transform.scale(cursor_surf, new_cursor_size)
        cursor = pygame.cursors.Cursor((0, 0), cursor_surf)
        pygame.mouse.set_cursor(cursor)

        # Selection index
        self.item_selection_index = 0

        # Menu
        self.menu = Menu()

        # Placed tiles collection
        self.tiles_placed = {}

        # Tiles collection
        self.tiles_data = tiles_data

    def get_current_cell(self):
        distance_to_origin = Vector(mouse_position()) - self.origin

        if distance_to_origin.x > 0:
            col = int(distance_to_origin.x / TILE_SIZE)
        else:
            col = int(distance_to_origin.x / TILE_SIZE) - 1

        if distance_to_origin.y > 0:
            row = int(distance_to_origin.y / TILE_SIZE)
        else:
            row = int(distance_to_origin.y / TILE_SIZE) - 1
        return col, row

    # Event loop
    def event_loop(self):
        # Event loop
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # Quit the game
                pygame.quit()
                sys.exit()
            self.shift_process(event)  # Process possible shift
            self.menu_click(event)  # Process possible click on the menu

    # Input process (movement, click...)
    def shift_process(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[0] and pygame.key.get_pressed()[pygame.K_LCTRL]:  # Shift started
            self.mouse_clicked = True
            self.offset = Vector(mouse_position()) - self.origin
        if not pygame.mouse.get_pressed()[0]:  # Shift ended
            self.mouse_clicked = False

        # Shift update
        if self.mouse_clicked:
            self.origin = Vector(mouse_position()) - self.offset

        # Scrooling option
        if event.type == pygame.MOUSEWHEEL:
            if pygame.key.get_pressed()[pygame.K_LCTRL]:
                self.origin.y -= event.y * 50
            else:
                self.origin.x += event.y * 50

    def menu_click(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.menu.rect.collidepoint(mouse_position()):  # If menu clicked
            if new_selection_index := self.menu.click(mouse_position(), pygame.mouse.get_pressed()):
                self.item_selection_index = new_selection_index

    def tiles_adding(self):
        if pygame.mouse.get_pressed()[0] and not self.menu.rect.collidepoint(mouse_position()):
            current_cel = self.get_current_cell()

            if current_cel != self.last_selected_cell:
                if current_cel in self.tiles_placed:
                    self.tiles_placed[current_cel].add_id(self.item_selection_index)
                else:
                    self.tiles_placed[current_cel] = Tile(self.item_selection_index)
                self.last_selected_cell = current_cel
                self.check_neighbors(current_cel)

    # Drawing
    def draw_tiles_grid(self):
        cols = WINDOW_WIDTH // TILE_SIZE
        rows = WINDOW_HEIGHT // TILE_SIZE

        origin_offset = Vector(
            x=self.origin.x - int(self.origin.x / TILE_SIZE) * TILE_SIZE,
            y=self.origin.y - int(self.origin.y / TILE_SIZE) * TILE_SIZE
        )

        self.support_grid_surface.fill("green")

        for col in range(cols + 1):
            x = origin_offset.x + col * TILE_SIZE
            pygame.draw.line(self.support_grid_surface, LINE_COLOR, (x, 0), (x, WINDOW_HEIGHT))

        for row in range(rows + 1):
            y = origin_offset.y + row * TILE_SIZE
            pygame.draw.line(self.support_grid_surface, LINE_COLOR, (0, y), (WINDOW_WIDTH, y))

        self.display_surface.blit(self.support_grid_surface, (0, 0))

    def check_neighbors(self, cell):
        cluster_size = 3
        local_cluster = [
            (cell[0] + row - int(cluster_size/2), cell[1] + col - int(cluster_size/2))
            for row in range(cluster_size)
            for col in range(cluster_size)
        ]
        for cell in local_cluster:
            if cell in self.tiles_placed:
                self.tiles_placed[cell].terrain_neighbors = []
                for name, direction in NEIGHBOR_DIRECTIONS.items():
                    neighbor_cell = (cell[0] + direction[0], cell[1] + direction[1])
                    if neighbor_cell in self.tiles_placed:
                        if self.tiles_placed[neighbor_cell].has_terrain:
                            self.tiles_placed[cell].terrain_neighbors.append(name)

    def tiles_drawing(self):
        for pos, tile in self.tiles_placed.items():
            pos = self.origin + Vector(pos) * TILE_SIZE
            if tile.has_terrain:
                name = ''.join(tile.terrain_neighbors)
                terrain_style = name if name in self.tiles_data else '5'
                surf = pygame.transform.scale(self.tiles_data[terrain_style], (TILE_SIZE, TILE_SIZE))
                self.display_surface.blit(surf, pos)

    def run(self, dt):
        self.display_surface.fill('white')
        self.event_loop()

        # Drawings
        self.draw_tiles_grid()
        self.tiles_adding()
        self.tiles_drawing()
        self.menu.display(self.item_selection_index)
        pygame.draw.circle(self.display_surface, "blue", self.origin, 10)


class Tile:
    def __init__(self, tile_id):

        # Tile information
        self.has_terrain = False
        self.has_water = False
        self.water_on_top = False

        self.terrain_neighbors = []

        # Enemy
        self.enemy = None

        # Objects
        self.objects = []

        self.add_id(tile_id)

    def add_id(self, tile_id):
        data = {key: value['style'] for key, value in EDITOR_DATA.items()}
        match data[tile_id]:
            case 'terrain': self.has_terrain = True
            case 'water': self.has_water = True
            case 'enemy': self.enemy = tile_id
