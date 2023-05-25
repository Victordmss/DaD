from os import walk
import pygame


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
