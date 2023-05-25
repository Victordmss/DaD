from os import walk
import pygame
from PIL import Image


def import_folder(path):
    data = []
    for name, sub, images in walk(path):
        for image in images:
            full_path = path + '/' + image
            image_surface = pygame.image.load(full_path)
            data.append(image_surface)
    return data


def import_folder_dict(path):
    data = {}
    for name, sub, images in walk(path):
        for image in images:
            full_path = path + '/' + image
            image_surface = pygame.image.load(full_path)
            data[image.split(".")[0]] = image_surface
    return data


"""def create_png_every_32_pixels():
    image = Image.open('')
    width, height = image.size
    i = 0
    for x in range(0, width, 32):
        i += 1
        new_image = image.crop((x, 0, x+32, 32))
        new_image.save(f'resources/assets/player/{i}.png')
"""