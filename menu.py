import pygame
from settings import *
from pygame.math import Vector2 as Vector
from pygame.image import load


class Menu:
    def __init__(self):
        self.display_surface = pygame.display.get_surface()
        self.create_data()
        self.create_buttons()

    def create_data(self):
        self.menu_surfaces = {}
        for key, value in EDITOR_DATA.items():
            if value["menu"]:
                if not value["menu"] in self.menu_surfaces:
                    self.menu_surfaces[value["menu"]] = [(key, load(value['menu_surf']))]
                else:
                    self.menu_surfaces[value["menu"]].append((key, load(value['menu_surf'])))

    def create_buttons(self):

        # Menu area
        size = Vector(200, 300)
        margin = 6
        top_left = (WINDOW_WIDTH - size.x - margin, margin)
        self.rect = pygame.Rect(top_left, size)

        # Buttons area
        self.button_rect_template = pygame.Rect(self.rect.topleft, (self.rect.width / 2, self.rect.height / 3))
        button_margin = 5

        self.buttons = {
            1: {
                'terrain': self.button_rect_template.copy().inflate(-button_margin, -button_margin),
                'tree': self.button_rect_template.move(0, self.button_rect_template.width).inflate(-button_margin,-button_margin),
                'box': self.button_rect_template.move(0, self.button_rect_template.width * 2).inflate(-button_margin, -button_margin),
                'sign': self.button_rect_template.move(self.button_rect_template.height, 0).inflate(-button_margin, -button_margin),
                'pot': self.button_rect_template.move(self.button_rect_template.height, self.button_rect_template.width).inflate(-button_margin, -button_margin),
                'spike': self.button_rect_template.move(self.button_rect_template.height, self.button_rect_template.width * 2).inflate(-button_margin, -button_margin),
            }
        }
        self.buttons_group = pygame.sprite.Group()
        for key, button in self.buttons[1].items():
            Button(button, self.buttons_group, self.menu_surfaces[key])

    def click(self, pos, mouse_button):
        for sprite in self.buttons_group:
            if sprite.rect.collidepoint(pos):
                if mouse_button[2]:
                    sprite.switch()
                print(sprite.get_id())
                return sprite.get_id()

    def highlight_indicator(self, index):
        for key, button in self.buttons[1].items():
            if EDITOR_DATA[index]['menu'] == key:
                pygame.draw.rect(self.display_surface, BUTTON_LINE_COLOR, self.buttons[1][key].inflate(4, 4), 5, 4)

    def display(self, index):
        # pygame.draw.rect(self.display_surface, 'grey', self.rect)
        #for button in self.buttons[1].values():
            #pygame.draw.rect(self.display_surface, 'yellow', button)
        self.buttons_group.update()
        self.buttons_group.draw(self.display_surface)
        self.highlight_indicator(index)


class Button(pygame.sprite.Sprite):
    def __init__(self, rect, group, items, items_click=None):
        super().__init__(group)
        self.image = pygame.Surface(rect.size)
        self.rect = rect
        # Items
        self.items = items
        self.index = 0
        self.main_active = True

    def get_id(self):
        return self.items[self.index][0]

    def switch(self):
        self.index += 1
        self.index = 0 if self.index >= len(self.items) else self.index

    def update(self):
        self.image.fill(BUTTON_BG_COLOR)
        surf = self.items[self.index][1]
        new_surf_size = (60, 60)
        surf = pygame.transform.scale(surf, new_surf_size)
        rect = surf.get_rect(center=(self.rect.width / 2, self.rect.height / 2))
        self.image.blit(surf, rect)
