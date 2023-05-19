import pygame, sys
from settings import *
from editor import Editor
from os import walk

class Main:
    def __init__(self):
        pygame.init()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()
        self.import_data()
        self.editor = Editor(self.tiles_data)  # Init the editor of the game

    def import_data(self):
        self.tiles_data = self.import_folder_dict('resources/assets/blocks/terrain')

    def import_folder(self, path):
        data = []
        for name, sub, images in walk(path):
            for image in images:
                full_path = path + '/' + image
                image_surface = pygame.image.load(full_path)
                data.append(image_surface)
        return data

    def import_folder_dict(self, path):
        data = {}
        for name, sub, images in walk(path):
            for image in images:
                full_path = path + '/' + image
                image_surface = pygame.image.load(full_path)
                data[image.split(".")[0]] = image_surface
        return data

    def run(self):
        while True:
            dt = self.clock.tick() / 1000

            self.editor.run(dt)
            pygame.display.update()


if __name__ == '__main__':
    main = Main()
    main.run()