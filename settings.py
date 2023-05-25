WINDOW_HEIGHT = 720
WINDOW_WIDTH = 1280
TILE_SIZE = 64
LINE_COLOR = "Black"
ANIMATION_SPEED = 8

EDITOR_DATA = {
    0: {'style': 'player', 'type': 'object', 'menu': None, 'menu_surf': None,
        'preview': None, 'graphics': 'resources/assets/player/cat_no_movement'},
    1: {'style': 'sky', 'type': 'object', 'menu': None, 'menu_surf': None,
        'preview': None, 'graphics': None},

    2: {'style': 'terrain', 'type': 'tile', 'menu': 'terrain', 'menu_surf': 'resources/assets/blocks/terrain/X.png',
        'preview': 'resources/assets/blocks/terrain/X.png', 'graphics': None},

    3: {'style': 'tree', 'type': 'object', 'menu': 'tree',
        'menu_surf': 'resources/assets/decorations/nature/tree1.png',
        'preview': 'resources/assets/decorations/nature/tree1.png', 'graphics': None},
    4: {'style': 'tree', 'type': 'object', 'menu': 'tree',
        'menu_surf': 'resources/assets/decorations/nature/tree2.png',
        'preview': 'resources/assets/decorations/nature/tree2.png', 'graphics': None},
    5: {'style': 'tree', 'type': 'object', 'menu': 'tree',
        'menu_surf': 'resources/assets/decorations/nature/tree3.png',
        'preview': 'resources/assets/decorations/nature/tree3.png', 'graphics': None},

    6: {'style': 'pot', 'type': 'tile', 'menu': 'pot',
        'menu_surf': 'resources/assets/decorations/pot1.png',
        'preview': 'resources/assets/decorations/pot1.png', 'graphics': None},

    7: {'style': 'pot', 'type': 'tile', 'menu': 'pot',
        'menu_surf': 'resources/assets/decorations/pot2.png',
        'preview': 'resources/assets/decorations/pot2.png', 'graphics': None},

    8: {'style': 'pot', 'type': 'tile', 'menu': 'pot',
        'menu_surf': 'resources/assets/decorations/pot3.png',
        'preview': 'resources/assets/decorations/pot3.png', 'graphics': None},

    9: {'style': 'sign', 'type': 'object', 'menu': 'sign',
        'menu_surf': 'resources/assets/decorations/sign1.png',
        'preview': 'resources/assets/decorations/sign1.png', 'graphics': None},
    10: {'style': 'sign', 'type': 'object', 'menu': 'sign',
         'menu_surf': 'resources/assets/decorations/sign2.png',
         'preview': 'resources/assets/decorations/sign2.png', 'graphics': None},

    11: {'style': 'box', 'type': 'tile', 'menu': 'box',
         'menu_surf': 'resources/assets/decorations/box1.png',
         'preview': 'resources/assets/decorations/box1.png', 'graphics': None},
    12: {'style': 'box', 'type': 'tile', 'menu': 'box',
         'menu_surf': 'resources/assets/decorations/box2.png',
         'preview': 'resources/assets/decorations/box2.png', 'graphics': None},
    13: {'style': 'box', 'type': 'tile', 'menu': 'box',
         'menu_surf': 'resources/assets/decorations/box3.png',
         'preview': 'resources/assets/decorations/box3.png', 'graphics': None},

    14: {'style': 'spike', 'type': 'tile', 'menu': 'spike',
         'menu_surf': 'resources/assets/decorations/enemy/spikes.png',
         'preview': 'resources/assets/decorations/enemy/spikes.png', 'graphics': None},
}


BUTTON_LINE_COLOR = '#f5f1de'
BUTTON_BG_COLOR = '#33323d'

NEIGHBOR_DIRECTIONS = {
    '1': (0, -1),
    '2': (1, -1),
    '3': (1, 0),
    '4': (1, 1),
    '5': (0, 1),
    '6': (-1, 1),
    '7': (-1, 0),
    '8': (-1, -1)
}
