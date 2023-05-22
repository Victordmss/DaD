import pygame, sys
from pygame.math import Vector2 as Vector
from pygame.mouse import get_pos as mouse_position
from pygame.image import load
from settings import *
from menu import Menu


# This method is used to know is "what" is in "where"
def in_container(what: str, where: str) -> bool:
    for thing in what:
        if thing not in where:
            return False
    return True


# This class manage the use and all the processes of the editor in the game
class Editor:
    def __init__(self, tiles_data):
        # Window setup
        self.display_surface = pygame.display.get_surface()

        # Navigation
        self.origin = Vector()  # origin point of the current window
        self.mouse_clicked = False
        self.offset = Vector(0, 0)  # Movement value in the 2D spaces
        self.tile_size = TILE_SIZE

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

        # Adding tiles parameters
        self.item_selection_index = 0
        self.last_selected_cell = None  # For now, there is no last selected cell
        self.tiles_placed = {}
        self.tiles_data = tiles_data

        # Menu
        self.menu = Menu()

    # Drawing the additional grid that helps the user to know where he can place tiles
    def draw_tiles_grid(self):
        cols = WINDOW_WIDTH // self.tile_size
        rows = WINDOW_HEIGHT // self.tile_size

        # Calculate the offset from the origin to align the grid properly
        origin_offset = Vector(
            x=self.origin.x - int(self.origin.x / self.tile_size) * self.tile_size,
            y=self.origin.y - int(self.origin.y / self.tile_size) * self.tile_size
        )

        # Fill the support grid surface with green color
        self.support_grid_surface.fill("green")

        # Draw vertical grid lines
        for col in range(cols + 1):
            x = origin_offset.x + col * self.tile_size
            pygame.draw.line(self.support_grid_surface, LINE_COLOR, (x, 0), (x, WINDOW_HEIGHT))

        # Draw horizontal grid lines
        for row in range(rows + 1):
            y = origin_offset.y + row * self.tile_size
            pygame.draw.line(self.support_grid_surface, LINE_COLOR, (0, y), (WINDOW_WIDTH, y))

        # Blit the support grid surface onto the display surface
        self.display_surface.blit(self.support_grid_surface, (0, 0))

    def run(self, dt):
        self.event_loop()

        # Drawings
        self.display_surface.fill("#25282d")
        self.draw_tiles_grid()
        self.tiles_adding()
        self.tiles_drawing()
        self.menu.display(self.item_selection_index)

    # Event loop
    def event_loop(self):
        # Event loop
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # Quit the game
                pygame.quit()
                sys.exit()
            self.shift_process(event)  # Process possible shift
            self.menu_click(event)  # Process possible click on the menu
            self.tiles_adding()  # Process adding of tiles
            self.tiles_removing()  # Process removing of tiles
            self.zoom_process(event)  # Process the zoom of the window

    def zoom_process(self, event):
        if event.type == pygame.MOUSEWHEEL and pygame.key.get_pressed()[pygame.K_LCTRL]:
            if 10 <= self.tile_size <= 100:
                self.tile_size += event.y * int(self.tile_size / 10)
            elif self.tile_size <= 10 and event.y > 0:
                self.tile_size += event.y * int(self.tile_size / 10)
            elif self.tile_size >= 100 and event.y < 0:
                self.tile_size += event.y * int(self.tile_size / 10)

    # This method is used to know if the user has clicked on the menu
    def menu_click(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.menu.rect.collidepoint(mouse_position()):  # If menu clicked
            if new_selection_index := self.menu.click(mouse_position(), pygame.mouse.get_pressed()):
                self.item_selection_index = new_selection_index

    # This method helps us to know which tiles have been touched on the grid of the editor window
    def get_current_cell(self):
        # Calculate the distance from the mouse position to the origin
        distance_to_origin = Vector(mouse_position()) - self.origin

        # Calculate the column index of the current cell
        if distance_to_origin.x > 0:
            col = int(distance_to_origin.x / self.tile_size)
        else:
            col = int(distance_to_origin.x / self.tile_size) - 1

        # Calculate the row index of the current cell
        if distance_to_origin.y > 0:
            row = int(distance_to_origin.y / self.tile_size)
        else:
            row = int(distance_to_origin.y / self.tile_size) - 1

        return col, row

    # Input process (movement, click...)
    def shift_process(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN \
                and pygame.mouse.get_pressed()[0] \
                and pygame.key.get_pressed()[pygame.K_LCTRL]:  # Shift started
            self.mouse_clicked = True
            self.offset = Vector(mouse_position()) - self.origin

        if not pygame.mouse.get_pressed()[0]:  # Shift ended
            self.mouse_clicked = False

        # Shift update
        if self.mouse_clicked:
            self.origin = Vector(mouse_position()) - self.offset

        # Scrolling option
        if event.type == pygame.MOUSEWHEEL and not pygame.key.get_pressed()[pygame.K_LCTRL]:
            if pygame.key.get_pressed()[pygame.K_LSHIFT]:
                self.origin.y -= event.y * 50
            else:
                self.origin.x += event.y * 50

    # This method is used to add new tiles on the editor window
    def tiles_adding(self):
        # Check if the left mouse button is pressed, not over the menu, and not holding the left Control key (movement)
        if pygame.mouse.get_pressed()[0] \
                and not self.menu.rect.collidepoint(mouse_position()) \
                and not pygame.key.get_pressed()[pygame.K_LCTRL]:
            current_cel = self.get_current_cell()

            # Check if the current cell is different from the last selected cell (optimisation verification)
            if current_cel != self.last_selected_cell:
                if current_cel in self.tiles_placed:
                    # Add the item_selection_index to the existing tile at the current cell
                    self.tiles_placed[current_cel].add_id(self.item_selection_index)
                else:
                    # Create a new tile at the current cell with the item_selection_index
                    self.tiles_placed[current_cel] = Tile(self.item_selection_index)

                self.last_selected_cell = current_cel
                self.check_neighbors(current_cel)  # Updating the shape of the terrain tiles

    # Draw the tiles on the editor window
    def tiles_drawing(self):
        for pos, tile in self.tiles_placed.items():
            pos = self.origin + Vector(pos) * self.tile_size
            if tile.has_terrain:
                name = ''.join(tile.terrain_neighbors)
                terrain_style = name if name in self.tiles_data else 'X'  # X is the default terrain file
                surf = pygame.transform.scale(self.tiles_data[terrain_style], (self.tile_size, self.tile_size))
                self.display_surface.blit(surf, pos)

    # This method is used to delete tiles on the editor window
    def tiles_removing(self):
        # Check if the right mouse button is pressed and not over the menu
        if pygame.mouse.get_pressed()[2] and not self.menu.rect.collidepoint(mouse_position()):
            if self.tiles_placed:
                current_cel = self.get_current_cell()

                # Check if the current cell exists in the tiles_placed dictionary
                if current_cel in self.tiles_placed:
                    # Remove the item_selection_index from the tile at the current cell
                    self.tiles_placed[current_cel].remove_id(self.item_selection_index)

                    # Check if the tile at the current cell becomes empty
                    if self.tiles_placed[current_cel].is_empty:
                        # If the tile is empty, remove it from the tiles_placed dictionary
                        del self.tiles_placed[current_cel]

                    self.check_neighbors(current_cel)

    # Method used to update the shape of the displayed tile
    def check_neighbors(self, cell):

        # The convention used allows us to identify the desired shape of the tile.
        # Each number represents a specific neighbor position. (Look at the convention in settings.py)
        # We add in the name of the cell the representative number of each neighbouring cell that has a placed tile
        # The name obtained is directly linked with a png file that represent the good sprite.

        cluster_size = 3
        # Create a local cluster of cells around the given cell
        local_cluster = [
            (cell[0] + row - int(cluster_size / 2), cell[1] + col - int(cluster_size / 2))
            for row in range(cluster_size)
            for col in range(cluster_size)
        ]

        for cell in local_cluster:
            if cell in self.tiles_placed:
                # Clear the terrain code for the current cell
                self.tiles_placed[cell].terrain_neighbors = ""

                # Check neighboring cells in all directions
                for name, direction in NEIGHBOR_DIRECTIONS.items():
                    neighbor_cell = (cell[0] + direction[0], cell[1] + direction[1])
                    if neighbor_cell in self.tiles_placed:
                        if self.tiles_placed[neighbor_cell].has_terrain:
                            # Append the direction name to the terrain_neighbors string if the neighboring cell has terrain
                            self.tiles_placed[cell].terrain_neighbors += name

                self.remove_duplicate(cell)

    # Check and remove duplicate entries from the terrain_neighbors string of the given cell
    def remove_duplicate(self, cell):
        if not in_container("13", self.tiles_placed[cell].terrain_neighbors):
            self.tiles_placed[cell].terrain_neighbors = self.tiles_placed[cell].terrain_neighbors.replace("2", "")
        if not in_container("35", self.tiles_placed[cell].terrain_neighbors):
            self.tiles_placed[cell].terrain_neighbors = self.tiles_placed[cell].terrain_neighbors.replace("4", "")
        if not in_container("57", self.tiles_placed[cell].terrain_neighbors):
            self.tiles_placed[cell].terrain_neighbors = self.tiles_placed[cell].terrain_neighbors.replace("6", "")
        if not in_container("17", self.tiles_placed[cell].terrain_neighbors):
            self.tiles_placed[cell].terrain_neighbors = self.tiles_placed[cell].terrain_neighbors.replace("8", "")


class Tile:
    def __init__(self, tile_id):
        # Tile information
        self.has_terrain = False  # Flag indicating if the tile has terrain
        self.is_empty = False  # Flag indicating if the tile is empty
        self.enemy = None  # Flag indicating if the tile is an enemy

        self.terrain_neighbors = []  # List of terrain neighbors
        self.objects = []  # List of objects on the tile

        self.add_id(tile_id)  # Add the initial tile ID

    def add_id(self, tile_id):
        data = {key: value['style'] for key, value in EDITOR_DATA.items()}
        # Match the tile_id with the corresponding style in the data dictionary
        match data[tile_id]:
            case 'terrain':
                self.has_terrain = True
            case 'enemy':
                self.enemy = tile_id

    def check_content(self):
        # Check the content of the tile and update the is_empty flag
        if not self.has_terrain and not self.enemy:
            self.is_empty = True

    def remove_id(self, tile_id):
        data = {key: value['style'] for key, value in EDITOR_DATA.items()}
        # Match the tile_id with the corresponding style in the data dictionary
        match data[tile_id]:
            case 'terrain':
                self.has_terrain = False
            case 'enemy':
                self.enemy = None
        self.check_content()
