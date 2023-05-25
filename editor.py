import pygame, sys
from pygame.math import Vector2 as Vector
from pygame.mouse import get_pos as mouse_position
from pygame.image import load
from settings import *
from support import *
from menu import Menu
import random

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
        self.imports()

        # Menu
        self.menu = Menu()

        # Object
        self.objects_placed = pygame.sprite.Group()

        # Player
        Object(
            pos=(200, WINDOW_HEIGHT / 2),
            frame=self.animations[0]['frames'],
            tile_id=0,
            origin=self.origin,
            group=self.objects_placed
        )
        self.object_selected = False

    def imports(self):

        # animations
        self.animations = {}
        for key, value in EDITOR_DATA.items():
            if value['graphics']:
                graphics = import_folder(value['graphics'])
                self.animations[key] = {
                    'frame index': 0,
                    'frames': graphics,
                    'length': len(graphics)
                }

        for key, value in EDITOR_DATA.items():
            if value['type'] == 'tile' and value["style"] != "terrain":
                image_surface = pygame.image.load(value['menu_surf'])
                self.tiles_data[value["menu_surf"].split(".")[-2].split('/')[-1]] = image_surface

    def animation_update(self, dt):
        for value in self.animations.values():
            value['frame index'] += ANIMATION_SPEED * dt
            if value['frame index'] >= value['length']:
                value['frame index'] = 0

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
        self.display_surface.fill('#92a9ce')
        self.draw_tiles_grid()
        self.canvas_adding()
        self.draw_level()
        self.menu.display(self.item_selection_index)

        # Animations
        self.animation_update(dt)
        for canvas_object in self.objects_placed:
            canvas_object.update(dt)

    # Event loop
    def event_loop(self):
        # Event loop
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # Quit the game
                pygame.quit()
                sys.exit()
            self.shift_process(event)  # Process possible shift
            self.menu_click(event)  # Process possible click on the menu
            self.object_dragging(event)
            self.canvas_adding()  # Process adding of tiles
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
            for sprite_object in self.objects_placed:
                sprite_object.shift_position(self.origin)

        # Scrolling option
        if event.type == pygame.MOUSEWHEEL and not pygame.key.get_pressed()[pygame.K_LCTRL]:
            if pygame.key.get_pressed()[pygame.K_LSHIFT]:
                self.origin.y -= event.y * 50
            else:
                self.origin.x += event.y * 50

    def object_dragging(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[0]:
            for sprite in self.objects_placed:
                if sprite.rect.collidepoint(event.pos):
                    self.object_selected = True
                    sprite.start_drag()

        if event.type == pygame.MOUSEBUTTONUP and self.object_selected:
            for sprite in self.objects_placed:
                if sprite.selected:
                    sprite.end_drag(self.origin)
                    self.object_selected = False

    # This method is used to add new tiles on the editor window
    def canvas_adding(self):
        # Check if the left mouse button is pressed, not over the menu, and not holding the left Control key (movement)
        if pygame.mouse.get_pressed()[0] \
                and not self.menu.rect.collidepoint(mouse_position()) \
                and not pygame.key.get_pressed()[pygame.K_LCTRL]\
                and not self.object_selected:

            current_cel = self.get_current_cell()

            if EDITOR_DATA[self.item_selection_index]['type'] == "tile": # Let's place a new tile
                # Check if the current cell is different from the last selected cell (optimisation verification)
                if current_cel != self.last_selected_cell:
                    if current_cel in self.tiles_placed:
                        # Add the item_selection_index to the existing tile at the current cell
                        self.tiles_placed[current_cel].tile_id = self.item_selection_index
                    else:
                        # Create a new tile at the current cell with the item_selection_index
                        self.tiles_placed[current_cel] = Tile(self.item_selection_index)

                    self.last_selected_cell = current_cel
                    self.check_neighbors(current_cel)  # Updating the shape of the terrain tiles

            else:   # Place a new object
                Object(
                    pos=mouse_position(),
                    frame=self.animations[self.item_selection_index]["frames"],
                    tile_id=self.item_selection_index,
                    origin=self.origin,
                    group=self.objects_placed
                )

    # Draw the tiles on the editor window
    def draw_level(self):
        # Objects
        self.objects_placed.draw(self.display_surface)

        # Tiles
        for pos, tile in self.tiles_placed.items():
            pos = self.origin + Vector(pos) * self.tile_size
            # Terrain
            match tile.tile_id:
                case 2:
                    name = ''.join(tile.terrain_neighbors)
                    terrain_style = name if name in self.tiles_data else 'X'  # X is the default terrain file
                    surf = pygame.transform.scale(self.tiles_data[terrain_style], (self.tile_size, self.tile_size))
                    self.display_surface.blit(surf, pos)

                case 6:
                    terrain_style = self.tiles_data[f'pot1']
                    surf = pygame.transform.scale(terrain_style,
                                                  (terrain_style.get_width() * 2, terrain_style.get_height() * 2))

                    if not tile.random_pos:
                        tile.random_pos = random.randint(0, int(self.tile_size - surf.get_width()))

                    self.display_surface.blit(surf, (pos[0] + tile.random_pos, pos[1] + (self.tile_size - surf.get_height())))

                case 7:
                    terrain_style = self.tiles_data['pot2']
                    surf = pygame.transform.scale(terrain_style,
                                                  (terrain_style.get_width() * 2, terrain_style.get_height() * 2))

                    if not tile.random_pos:
                        tile.random_pos = random.randint(0, int(self.tile_size - surf.get_width()))

                    self.display_surface.blit(surf,
                                              (pos[0] + tile.random_pos, pos[1] + (self.tile_size - surf.get_height())))

                case 8:
                    terrain_style = self.tiles_data['pot3']
                    surf = pygame.transform.scale(terrain_style,
                                                  (terrain_style.get_width() * 2, terrain_style.get_height() * 2))

                    if not tile.random_pos:
                        tile.random_pos = random.randint(0, int(self.tile_size - surf.get_width()))

                    self.display_surface.blit(surf,
                                              (pos[0] + tile.random_pos, pos[1] + (self.tile_size - surf.get_height())))

                case 11:
                    terrain_style = self.tiles_data['box1']
                    surf = pygame.transform.scale(terrain_style, (self.tile_size, self.tile_size))
                    self.display_surface.blit(surf, pos)

                case 12:
                    terrain_style = self.tiles_data['box2']
                    surf = pygame.transform.scale(terrain_style, (self.tile_size, self.tile_size))
                    self.display_surface.blit(surf, pos)

                case 13:
                    terrain_style = self.tiles_data['box3']
                    surf = pygame.transform.scale(terrain_style, (self.tile_size * 0.90, self.tile_size * 1.05))
                    self.display_surface.blit(surf, pos)

                case 14:
                    terrain_style = self.tiles_data['spikes']
                    surf = pygame.transform.scale(terrain_style, (self.tile_size, int(self.tile_size / terrain_style.get_width() * terrain_style.get_height())))
                    self.display_surface.blit(surf, (pos[0], pos[1] + self.tile_size - surf.get_height()))

    # This method is used to delete tiles on the editor window
    def tiles_removing(self):
        # Check if the right mouse button is pressed and not over the menu
        if pygame.mouse.get_pressed()[2] and not self.menu.rect.collidepoint(mouse_position()):
            if self.tiles_placed:
                current_cel = self.get_current_cell()

                # Check if the current cell exists in the tiles_placed dictionary
                if current_cel in self.tiles_placed:
                    # Remove the item_selection_index from the tile at the current cell
                    self.tiles_placed[current_cel].remove_id()

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
                        if self.tiles_placed[neighbor_cell].tile_id == 2:
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
        self.tile_id = tile_id
        self.is_empty = False

        self.terrain_neighbors = []  # List of terrain neighbors
        self.objects = []  # List of objects on the tile

        self.random_pos = None

    def remove_id(self):
        self.tile_id = None
        self.is_empty = True


class Object(pygame.sprite.Sprite):
    def __init__(self, pos, frame, tile_id, origin, group):
        super().__init__(group)
        self.tile_id = tile_id

        # Animation
        self.frames = frame
        self.frame_index = 0

        self.image = self.set_image()
        self.rect = self.image.get_rect(center=pos)

        # movement
        self.distance_to_origin = Vector(self.rect.topleft - origin)
        self.selected = False
        self.mouse_offset = Vector(0, 0)

    def start_drag(self):
        self.selected = True
        self.mouse_offset = Vector(mouse_position()) - Vector(self.rect.topleft)

    def drag(self):
        if self.selected:
            self.rect.topleft = mouse_position() - self.mouse_offset

    def end_drag(self, origin):
        self.selected = False
        self.distance_to_origin = Vector(self.rect.topleft) - origin

    def set_image(self):
        image = self.frames[int(self.frame_index)]

        image_ratio = image.get_width() / image.get_height()

        if self.tile_id == 0:
            if image_ratio > 1:
                new_image_size = (TILE_SIZE, TILE_SIZE / image_ratio)
            else:
                new_image_size = (TILE_SIZE * image_ratio, TILE_SIZE)
            image = pygame.transform.scale(image, new_image_size)

        elif self.tile_id in [9, 10]:
            if image_ratio > 1:
                new_image_size = (2 * TILE_SIZE, 2 * TILE_SIZE / image_ratio)
            else:
                new_image_size = (2 * TILE_SIZE * image_ratio, 2 * TILE_SIZE)
            image = pygame.transform.scale(image, new_image_size)

        elif self.tile_id in [3, 4]:
            if image_ratio > 1:
                new_image_size = (4 * TILE_SIZE, 4 * TILE_SIZE / image_ratio)
            else:
                new_image_size = (4 * TILE_SIZE * image_ratio, 4 * TILE_SIZE)
            image = pygame.transform.scale(image, new_image_size)


        return image

    def animate(self, dt):
        self.frame_index += ANIMATION_SPEED * dt
        if self.frame_index >= len(self.frames):
            self.frame_index = 0
        self.image = self.set_image()
        self.rect = self.image.get_rect(midbottom=self.rect.midbottom)

    def shift_position(self, origin):
        self.rect.topleft = origin + self.distance_to_origin

    def update(self, dt):
        self.animate(dt)
        self.drag()




