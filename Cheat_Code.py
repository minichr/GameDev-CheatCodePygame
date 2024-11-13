#!/usr/bin/env python3
import pygame as p
from pygame.locals import *
import sys
import time 
import random as rm
from math import sin, cos, pi


p.mixer.init(44100, 16, 2, 4096)
p.init()

#Screen Details
windowx = 1050
windowy = 650
display = p.display.set_mode((windowx,windowy))
p.display.set_caption('Cheat Code')
t = p.time.Clock()
fps = 200
speed = 1

#Music Initialization

p.mixer.music.load('bg_music.mp3')
p.mixer.music.set_volume(0.09)
p.mixer.music.play(-1)

#Grid
tile = 50
gridl = windowx/tile
gridh = windowy/tile

#Overworld Pics + details
face  = p.transform.scale(p.image.load('char.png'), (tile,tile))
hitbox = p.Rect(0,0, tile-30,tile-30)

obj = p.transform.scale(p.image.load('files.png'), (tile,tile))
exit = p.transform.scale(p.image.load('terminal.png'), (tile,tile))
wall = p.transform.scale(p.image.load('First part.png'), (tile,tile))
enemy = p.transform.scale(p.image.load('enemy.png'), (tile,tile))

plus_HP = p.transform.scale(p.image.load('Slide1.png'), (600,300))
minus_HP = p.transform.scale(p.image.load('Slide2.png'), (600,300))
plus_amr = p.transform.scale(p.image.load('Slide3.png'), (600,300))
minus_amr = p.transform.scale(p.image.load('Slide4.png'), (600,300))
plus_pts = p.transform.scale(p.image.load('Slide5.png'), (600,300))
plus_dmg = p.transform.scale(p.image.load('Slide6.png'), (600,300))
amr_full = p.transform.scale(p.image.load('Slide7.png'), (600,300))
note = p.transform.scale(p.image.load('Slide8.png'), (560,70))


white = (200,200,200)
black = (0,0,0)
red = (255,80,80)
pastel_red = (240,170,150)
gray = (150, 150, 150)
white_light = (255, 255, 255)
GREEN = (0, 255, 0)

PLAY_AREA = 0
PLAY_WALL = 1
PLAY_ITEM = 2
PLAY_MONSTER = 3
PLAY_CHARACTER = 4
PLAY_EXIT = 5

#Background Pre-game
START_BG = 'start_bg.png'
BGSetting_IMG = 'settings_bg.png'
INSTRUCTIONS_BG = 'instructions_bg.png'
LEADERBOARD_BG = 'leaderboard_bg.png'

SCORES_FILE = 'score_record.txt'

#Battle Pics
loading = p.transform.scale(p.image.load('loading_bg.png'), (windowx,windowy))
battle_bg = p.transform.scale(p.image.load('fight2_bg.png'), (windowx,windowy))
floor_bg = p.transform.scale(p.image.load('floor_bg.png'), (windowx,windowy))
postgame_bg = p.transform.scale(p.image.load('stat_bbg.png'), (windowx,windowy))
bg = p.transform.scale(p.image.load('you win.jpg'), (windowx,windowy))
enemy_face = p.transform.scale(p.image.load('eyes.png'), (140,140))
bg2 = p.transform.scale(p.image.load('Game Over.png'), (windowx,windowy))

player_face = p.transform.scale(p.image.load('player.png'), (140,140))
attack = p.transform.scale(p.image.load('attack.png'), (90,90))
block = p.transform.scale(p.image.load('block.png'), (80,70))
dodge = p.transform.scale(p.image.load('dodge.png'), (90,80))
run = p.transform.scale(p.image.load('run.png'), (90,95))

#---
univ_font = p.font.Font('freesansbold.ttf', 25)


#########################################################################
class maps(object):
    def __init__(self, lvl):
        self.lvl = lvl
        if lvl == 1:
            self.w = int(gridl) - 4
            self.h = int(gridh)
        elif lvl == 2:
            self.w = int(gridl) - 2
            self.h = int(gridh)
        elif lvl == 3:
            self.w = int(gridl)
            self.h = int(gridh)
        self.t = tile
        self.g = None
        self.wa = None
        self.en = None
        self.e = None
        self.make_maze()
        self.rand_pos()

    def the_map(self):
        for row,tiles in enumerate(self.maze):
            for col, tile in enumerate(tiles):
                if tile == 1:
                    self.wa = walls(col,row)
                    allsprites.add(self.wa)
                    allwalls.add(self.wa)
                elif tile == 2:
                    self.item = items(col,row)
                    allsprites.add(self.item)
                    allitems.add(self.item)
                elif tile == 3:
                    self.en = enemies(col,row)
                    allsprites.add(self.en)
                    allenemies.add(self.en)
                elif tile == 4:
                    if self.lvl > 1:
                        self.g = player(col,row, HP, dmg, amr, pts, lvl)
                        allsprites.add(self.g)
                    else:
                        self.g = player(col, row)
                        allsprites.add(self.g)
                elif tile == 5:
                    self.e = exits(col,row)
                    allsprites.add(self.e)
                    allexit.add(self.e)
                p.mixer.music.load('Factory.ogg')
                p.mixer.music.set_volume(0.2)
                p.mixer.music.play(-1)

    def create_grid(self):
        grid = []

        for row in range(self.h):
            grid.append([])
            for column in range(self.w):
                if column % 2 == 1 and row % 2 == 1:
                    grid[row].append(PLAY_AREA)
                elif column == 0 or row == 0 or column == (self.h - 1) or row == (self.w - 1):
                    grid[row].append(PLAY_WALL)
                else:
                    grid[row].append(PLAY_WALL)
        return grid

    def make_maze(self):
        self.maze = self.create_grid()

        w = (len(self.maze[0]) - 1) // 2
        h = (len(self.maze) - 1) // 2
        self.visited = [[0] * w + [1] for _ in range(h)] + [[1] * (w +1)]

        self.walk(rm.randrange(w), rm.randrange(h))

    def walk(self, x, y):
        self.visited[y][x] = 1

        # random adjacent coordinate traversal
        d = [(x - 1, y), (x, y + 1), (x + 1, y), (x, y - 1)]
        rm.shuffle(d)

        for (xx, yy) in d:
            #if visited ignore
            if self.visited[yy][xx]:
                continue
            if xx == x:
                self.maze[max(y, yy) * 2][x * 2 + 1] = PLAY_AREA
            if yy == y:
                self.maze[y * 2 + 1][max(x, xx) * 2] = PLAY_AREA

            self.walk(xx, yy)

    def rand_pos(self):
        self.character = 0
        self.exit = 0
        if self.lvl == 1:
            self.items = rm.randint(2,6)
            self.monsters = rm.randint(1,2)
        elif self.lvl == 2:
            self.items = rm.randint(3,7)
            self.monsters = rm.randint(2,3)
        elif self.lvl == 3:
            self.items = rm.randint(4,8)
            self.monsters = rm.randint(3,4)
        while self.items:
            x, y = rm.randint(0, self.w-1), rm.randint(0, self.h-1)
            if not self.maze[y][x]:
                self.maze[y][x] = PLAY_ITEM
                self.items -= 1
        while not self.character:
            x, y = rm.randint(0, self.w-1), rm.randint(0, self.h-1)
            if not self.maze[y][x]:
                cx, cy = x, y
                self.maze[y][x] = PLAY_CHARACTER
                self.character += 1
        while not self.exit:
            x, y = rm.randint(0, self.w-1), rm.randint(0, self.h-1)
            if not self.maze[y][x] and x != cx and y != cy:
                self.maze[y][x] = PLAY_EXIT
                self.exit += 1
        while self.monsters:
            x, y = rm.randint(0, self.w-1), rm.randint(0, self.h-1)
            if not self.maze[y][x]:
                self.maze[y][x] = PLAY_MONSTER
                self.monsters -= 1
        print('Level', lvl)
        for x in self.maze:
            print(x)

#####################################################################

class player(p.sprite.Sprite):
    def __init__(self,x,y, HP = rm.randint(4,7), dmg = 3, amr = 0, pts = 0, lvl = 1):
        #Player Creation
        self.dx, self.dy, self.dz = 0, 0, 0
        i = rm.randint(0,3)
        randor = [0, pi/2, pi, 3*pi/2]
        self.orientation = randor[i]
        self.turn_left, self.turn_right = False, False
        self.move, self.a = 0,0
        self.trapped = False

        p.sprite.Sprite.__init__(self)
        self.image = face
        self.rect = self.image.get_rect()
        self.rect.x = x*tile
        self.rect.y = y*tile
        
        self.hitbox = hitbox
        self.posx, self.posy = self.rect.centerx, self.rect.centery
        self.hitbox.center = self.rect.center

        #Base Stats
        self.lvl = lvl
        self.HP = HP
        self.dmg = dmg
        self.amr = amr
        self.pts = pts
        

    def stats_overhead(self):
        #Display Stats while not battling
        font = p.font.Font('freesansbold.ttf', 25)
        HP = font.render('HP: ' + str(self.HP), True, black)
        dmg = font.render('Damage: ' + str(self.dmg), True, black)
        armor = font.render('Armor: ' + str(self.amr), True, black)
        pts = font.render('Points: ' + str(self.pts), True , black)
        lvl = font.render('Level: ' + str(self.lvl), True , black)
        display.blit(HP, (0, 0))
        display.blit(dmg, (0,22))
        display.blit(armor, (0,44))
        display.blit(pts, (450, 22))
        display.blit(lvl, (450,0))

    def stats_battle(self):
        #Display Stats while battling
        font = p.font.Font('freesansbold.ttf', 25)
        HP = font.render('HP: ' + str(self.HP), True, white)
        dmg = font.render('Damage: ' + str(self.dmg), True, white)
        armor = font.render('Armor: ' + str(self.amr), True, white)
        pts = font.render('Points: ' + str(self.pts), True , white)
        display.blit(HP, (windowx-320, 50))
        display.blit(dmg, (windowx-320,75))
        display.blit(armor, (windowx-320,100))
        display.blit(pts, (windowx-320, 125))

    def bump(self, allwalls, direction):
        #Wall Collision
        if direction == 'x':
            hits = p.sprite.spritecollide(self, allwalls, False, hbcollide)
            if hits:
                if self.dx > 0:
                    self.hitbox.right -= self.move
                if self.dx < 0:
                    self.hitbox.left += self.move
                self.move = 0
        if direction == 'y':
            hits = p.sprite.spritecollide(self, allwalls, False, hbcollide)
            if hits:
                if self.dy > 0:
                    self.hitbox.top -= self.move
                if self.dy < 0:
                    self.hitbox.bottom += self.move
                self.move = 0


    def pick(self, allitems):
        #Item Pickup
        pickup = p.sprite.spritecollide(self,allitems,True, hbcollide)
        font = p.font.Font('freesansbold.ttf', 50)
        for u in pickup:
            self.dx, self.dy, self.dz = 0, 0, 0
            self.turn_right, self.turn_left = False, False
            p.display.update()
            i = rm.randint(1,5)
            if i == 1:
                if self.amr < 7:
                    self.amr += rm.randrange(1,5)
                    display.blit(plus_amr, (windowx/4,windowy/4))
                if self.amr > 7:
                    a = self.amr - 7
                    self.amr = self.amr - a
                    display.blit(amr_full, (windowx/4,windowy/4))
            elif i == 2:
                self.HP += 2
                display.blit(plus_HP, (windowx/4,windowy/4))
            elif i == 3:
                self.dmg += rm.randrange(1,3)
                display.blit(plus_dmg, (windowx/4,windowy/4))
            elif i == 4:
                self.pts += rm.randrange(10,16)
                display.blit(plus_pts, (windowx/4,windowy/4))
            elif i == 5:
                if self.amr > 0:
                    self.amr -= round(0.6*self.amr)
                    display.blit(minus_amr, (windowx/4,windowy/4))
                else:
                    self.HP -= round(0.2*self.HP)
                    display.blit(minus_HP, (windowx/4,windowy/4))
            p.sprite.spritecollide(self,allitems,False)
            notified = True
            while notified:
                for event in p.event.get():
                    if event.type == p.KEYDOWN:
                        notified = False
                p.display.update()
            m.g.dz = 0
                
    def exit(self,allexit):
        #Exit Pickup
        pickup = p.sprite.spritecollide(self,allexit, False, hbcollide)
        if self.trapped and not pickup:
            self.trapped = False
        if not self.trapped:
            for u in pickup:
                self.dx, self.dy, self.dz = 0, 0, 0
                self.turn_right, self.turn_left = False, False
                p.display.update()
                font = p.font.Font('freesansbold.ttf', 35)
                yes = font.render('Press space to go to next level', True, black)
                display.blit(note, (windowx/4, windowy- 80))
                display.blit(yes, (windowx/4 +20, windowy- 60))
                for event in p.event.get():
                        if event.type == p.KEYDOWN:
                            if event.key == K_SPACE: #Key for interaction
                                m.g.lvl += 1
                                p.sprite.spritecollide(self,allitems,True, hbcollide)
                            else:
                                self.trapped = True
                break

    def engage(self, allenemies):
        #Fight Enemy
        battles = p.sprite.spritecollide(self,allenemies, True, hbcollide)
        for b in battles:
            self.dx, self.dy, self.dz = 0, 0, 0
            self.turn_right, self.turn_left = False, False
            p.display.update()
            battle()
            p.sprite.spritecollide(self,allenemies,False)
        m.g.dz = 0
        
            
class enemies(p.sprite.Sprite):
    def __init__(self,x,y):
        #Enemy Creation
        p.sprite.Sprite.__init__(self)
        self.image = enemy
        self.rect = self.image.get_rect()
        self.rect.x = x*tile
        self.rect.y = y*tile

        #Enemy Stats
        self.HP = rm.randrange(2,4)
        self.dmg = rm.randrange(1,3)
        self.amr = rm.randrange(0,2)

    def stats_battle(self):
        #Display Stats while battling
        font = p.font.Font('freesansbold.ttf', 25)
        HP = font.render('HP: ' + str(self.HP), True, white)
        dmg = font.render('Damage: ' + str(self.dmg), True, white)
        armor = font.render('Armor: ' + str(self.amr), True, white)
        display.blit(HP, (windowx-900, 50))
        display.blit(dmg, (windowx-900, 75))
        display.blit(armor, (windowx-900, 100))
        
class items(p.sprite.Sprite):
    def __init__(self,x,y):
        #Item Creation
        p.sprite.Sprite.__init__(self)
        self.image = obj
        self.rect = self.image.get_rect()
        self.rect.x = x*tile
        self.rect.y = y*tile
        
        
class walls(p.sprite.Sprite):
    def __init__(self,x,y):
        #Wall Creation
        p.sprite.Sprite.__init__(self)
        self.image = wall
        self.rect = self.image.get_rect()
        self.rect.x = x*tile
        self.rect.y = y*tile
        

class exits(p.sprite.Sprite):
    def __init__(self,x,y):
        #Exit Creation
        p.sprite.Sprite.__init__(self)
        self.image = exit
        self.rect = self.image.get_rect()
        self.rect.x = x*tile
        self.rect.y = y*tile
        
#############################################################
def draw():
    display.fill((120,120, 120))
    display.blit(floor_bg, (0,0))
    m.g.image = p.transform.rotate(face, (180*m.g.orientation/pi))
    m.g.rect = m.g.image.get_rect()
    m.g.rect.center = m.g.hitbox.center
    #p.draw.rect(display, (255,0,0), m.g.rect, 2)  #old hitbox representation
    p.draw.rect(display, white, m.g.hitbox, 2) #new hitbox representation
    allsprites.draw(display)
    allsprites.update()
    m.g.pick(allitems)
    m.g.exit(allexit)
    m.g.engage(allenemies)
    m.g.stats_overhead()
    p.display.update()

def gameover(x, time_elapsed):
    if x == 1:
        p.mixer.music.load('Factory.ogg')
        p.mixer.music.set_volume(0.09)
        p.mixer.music.play(-1)
        display.blit(bg, (0,0))
        font = p.font.Font('freesansbold.ttf', 100)
        mes = font.render('To be continued', True, gray)
        display.blit(mes, (windowx/8, windowy/2))
        notified = True
        while notified:
            for event in p.event.get():
                if event.type == QUIT:
                    p.quit()
                    sys.exit()
                if event.type == p.KEYDOWN:
                    if event.key == K_SPACE:
                        notified = False
            p.display.update()
            
    elif x == 2:
        display.blit(bg2, (0,0))
        font = p.font.Font('freesansbold.ttf', 100)
        mes = font.render('YOU ARE DEAD!', True, red) 
        display.blit(mes, (windowx/8, windowy/2))
        notified = True
        while notified:
            for event in p.event.get():
                if event.type == QUIT:
                    p.quit()
                    sys.exit()
                if event.type == p.KEYDOWN:
                    if event.key == K_SPACE:
                        notified = False
            p.display.update()
    post_game(time_elapsed)

def record_score(score_file, player_name, time, score):
    with open(score_file, 'a+') as fh:
        fh.write('\n' + str(player_name) + "|" + str(time) + "|" + str(score) + '\n')

def convert_time(milliseconds):
    seconds = milliseconds/1000
    hour = (seconds // 60) // 60
    mins = (seconds // 60) - (hour * 60)
    secs = (seconds % 60)
    
    time = str(int(hour)) + 'h:' + str(int(mins)) + 'm:' + str(int(secs)) + 's'
    return time
    
#Post Game
def post_game(time_elapsed):
    display.fill((75,185,75))
    font = p.font.Font('freesansbold.ttf', 80)
    p.display.update()
    
    #record score

    #convert time into appropriate time
    game_time = convert_time(time_elapsed)
    
    name = 0
    player_name = ''
    input_font = p.font.Font('freesansbold.ttf', 50)
    sc = input_font.render(str(m.g.pts), True, GREEN)
    display.blit(sc, (735, 135))
    time = input_font.render(str(game_time), True, GREEN)
    display.blit(time, (700, 280))
    notified = True
    while name == 0:
        display.blit(postgame_bg, (0,0))
        sc = input_font.render(str(m.g.pts), True, GREEN)
        display.blit(sc, (735, 135))
        time = input_font.render(str(game_time), True, GREEN)
        display.blit(time, (700, 280))
        for event in p.event.get():
            if event.type == QUIT:
                p.quit()
                sys.exit()
            elif event.type == p.KEYDOWN:
                if event.key == p.K_RETURN:
                    print('Input:', player_name) #tester
                    name = 1
                elif event.key == p.K_BACKSPACE:
                    player_name = player_name[:-1]
                else:
                    if len(player_name) < 7:
                        player_name += event.unicode
        name_surface = input_font.render(player_name, True, GREEN)
        display.blit(name_surface, (710, 450))
        p.display.update()
    p.mixer.music.load('bg_music.mp3')
    p.mixer.music.set_volume(0.09)
    p.mixer.music.play(-1)
    score  = str(m.g.pts)
    record_score(SCORES_FILE, player_name, game_time, score)
    Leaderboard(LEADERBOARD_BG, SCORES_FILE)

  
##############################################################
#Battle Stuff
def battle():
    pl_decision = ''
    en_decision = ' '
    text = ''
    choice = 0
    conflict = False
    battle_over = False
    eface = enemy_face
    pface = player_face
    win = False
    p_response, e_response = None, None
    p_dodged, en_dodged = False, False
    while not battle_over:
        t.tick(fps)
        display.blit(battle_bg, (0,0))
        m.g.stats_battle()
        m.en.stats_battle()
        font = p.font.Font('freesansbold.ttf', 50)
        letter = p.font.Font('freesansbold.ttf', 25)
        roundfont = p.font.Font('freesansbold.ttf', 80)
        mes = roundfont.render(text, True, white)
        display.blit(mes, (windowx/3 + 40, windowy/2 + 80))
        if p_response and e_response:
            p.draw.circle(display, (100,150,120), (windowx-380,windowy-350),tile)
            p.draw.circle(display, (100,150,120), (420,windowy-350),tile)
            display.blit(p_response, (windowx-423,windowy-385))
            display.blit(e_response, (378 ,windowy-385))
        
        p.draw.circle(display, (100,150,120), (150,windowy-100),tile)
        p.draw.circle(display, (100,150,120), (400,windowy-100),tile)
        p.draw.circle(display, (100,150,120), (650,windowy-100),tile)
        p.draw.circle(display, (100,150,120), (900,windowy-100),tile)

        display.blit(letter.render('Q', True, black), (144, windowy- 75)) #Q
        display.blit(letter.render('W', True, black), (391, windowy- 75)) #W
        display.blit(letter.render('E', True, black), (643, windowy- 75)) #E
        display.blit(letter.render('R', True, black), (897, windowy- 75)) #R
        yes = letter.render('Press SPACE to confirm', True, white)
        display.blit(yes, (windowx/3 +43, windowy- 30))
        
        p.draw.circle(display, (20,20,20), (windowx-820,windowy-350),100) #Enemy Circle
        p.draw.circle(display, gray, (windowx-190,windowy-350),100) #Player Circle
        display.blit(attack, (107,windowy-143))
        display.blit(block, (359,windowy-142))
        display.blit(dodge, (605,windowy-140))
        display.blit(run, (857,windowy-145))
        display.blit(eface, (windowx-888, windowy-423))
        display.blit(pface, (windowx-258, windowy-423))
        en_choices = ['attack', 'block', 'dodge']

        keys = p.key.get_pressed()
        if p_dodged:
            p_dodged = False
            if choice == 1:
                p.draw.circle(display, (200,250,220), (150,windowy-100),tile)
                display.blit(attack, (107,windowy-143))
                if keys[p.K_SPACE]:
                    pl_decision = 'attack'
                    p_response = attack
                    choice = 0
                    en_decision == rm.choice(('attack', 'dodge'))
                    conflict = True
                
            elif choice == 2:
                p.draw.circle(display, (200,250,220), (400,windowy-100),tile)
                display.blit(block, (359,windowy-142))
                if keys[p.K_SPACE]:
                    pl_decision = 'block'
                    p_response = block
                    choice = 0
                    en_decision == rm.choice(('attack', 'dodge'))
                    conflict = True
                    
            elif choice == 3:
                p.draw.circle(display, (200,250,220), (650,windowy-100),tile)
                display.blit(dodge, (605,windowy-140))
                if keys[p.K_SPACE]:
                    pl_decision = 'dodge'
                    p_response = dodge
                    en_decision = rm.choice(('attack', 'dodge'))
                    choice = 0
                    conflict = True

            elif choice == 4:
                p.draw.circle(display, (200,250,220), (900,windowy-100),tile)
                display.blit(run, (857,windowy-145))
                if keys[p.K_SPACE]:
                    battle_over = True
                    
            if en_decision == en_choices[0]:
                e_response = attack
            elif en_decision == en_choices[2]:
                e_response = dodge
                
            if conflict == True:
                if pl_decision == en_decision or pl_decision + en_decision == 'blockdodge':
                    if pl_decision + en_decision == 'attackattack':
                        dmg_enemy(2)
                        dmg_player()
                        text = 'Damage x2'
                    else:
                        text = None

                elif pl_decision + en_decision == 'dodgeattack':
                    chance = rm.randint(0,1)
                    if chance:
                        text = 'Dodged'
                        p_dodged = True
                    else:
                        dmg_player()
                        text = 'Dodge unsuccessful'

                elif pl_decision + en_decision == 'attackdodge':
                    chance = rm.randint(0,1)
                    if chance:
                        text = 'Hit x2'
                        en_dodged = True
                    else:
                        dmg_enemy(2)
                        text = 'Missed'
                elif pl_decision + en_decision == 'blockattack':
                    dmg_enemy(1, True)
                    dmg_player(0.5)
                    text = 'Blocked'
                    
        elif en_dodged:
            en_dodged = False
            if choice == 1:
                p.draw.circle(display, (200,250,220), (150,windowy-100),tile)
                display.blit(attack, (107,windowy-143))
                if keys[p.K_SPACE]:
                    pl_decision = 'attack'
                    p_response = attack
                    choice = 0
                    en_decision == rm.choice(en_choices)
                    conflict = True
                
            elif choice == 2:
                p.draw.circle(display, (200,250,220), (400,windowy-100),tile)
                display.blit(block, (357,windowy-140))
                if keys[p.K_SPACE]:
                    text = "You can't block"
                    
            elif choice == 3:
                p.draw.circle(display, (200,250,220), (650,windowy-100),tile)
                display.blit(dodge, (605,windowy-140))
                if keys[p.K_SPACE]:
                    pl_decision = 'dodge'
                    p_response = dodge
                    en_decision = rm.choice(en_choices)
                    choice = 0
                    conflict = True

            elif choice == 4:
                p.draw.circle(display, (200,250,220), (900,windowy-100),tile)
                display.blit(run, (857,windowy-145))
                if keys[p.K_SPACE]:
                    battle_over = True
                    
            if en_decision == en_choices[0]:
                e_response = attack
            elif en_decision == en_choices[1]:
                e_response = block
            elif en_decision == en_choices[2]:
                e_response = dodge
                
            if conflict == True:
                if pl_decision == en_decision or pl_decision + en_decision == 'dodgeblock' or pl_decision + en_decision == 'blockdodge':
                    if pl_decision + en_decision == 'attackattack':
                        dmg_enemy()
                        dmg_player(2)
                    text = None

                elif pl_decision + en_decision == 'dodgeattack':
                    chance = rm.randint(0,1)
                    if chance:
                        text = 'Dodged'
                        p_dodged = True
                    else:
                        dmg_player(2)
                        text = 'Dodge unsuccessful'

                elif pl_decision + en_decision == 'attackdodge':
                    chance = rm.randint(0,1)
                    if chance:
                        text = 'Hit'
                        en_dodged = True
                    else:
                        dmg_enemy()
                        text = 'Missed'

                elif pl_decision + en_decision == 'attackblock':
                    dmg_enemy(0.5)
                    dmg_player(1, True)
                    text = 'Blocked'

        else:
            if choice == 1:
                p.draw.circle(display, (200,250,220), (150,windowy-100),tile)
                display.blit(attack, (107,windowy-143))
                if keys[p.K_SPACE]:
                    pl_decision = 'attack'
                    p_response = attack
                    en_decision = rm.choice(en_choices)
                    choice = 0
                    conflict = True
                
            elif choice == 2:
                p.draw.circle(display, (200,250,220), (400,windowy-100),tile)
                display.blit(block, (359,windowy-142))
                if keys[p.K_SPACE]:
                    pl_decision = 'block'
                    p_response = block
                    en_decision = rm.choice(en_choices)
                    choice = 0
                    conflict = True
                    
            elif choice == 3:
                p.draw.circle(display, (200,250,220), (650,windowy-100),tile)
                display.blit(dodge, (605,windowy-140))
                if keys[p.K_SPACE]:
                    pl_decision = 'dodge'
                    p_response = dodge
                    en_decision = rm.choice(en_choices)
                    choice = 0
                    conflict = True

            elif choice == 4:
                p.draw.circle(display, (200,250,220), (900,windowy-100),tile)
                display.blit(run, (857,windowy-145))
                if keys[p.K_SPACE]:
                    battle_over = True
                    
            if en_decision == en_choices[0]:
                e_response = attack
            elif en_decision == en_choices[1]:
                e_response = block
            elif en_decision == en_choices[2]:
                e_response = dodge
                
            if conflict == True:
                if pl_decision == en_decision or pl_decision + en_decision == 'dodgeblock' or pl_decision + en_decision == 'blockdodge':
                    if pl_decision + en_decision == 'attackattack':
                        dmg_enemy()
                        dmg_player()
                    text = None

                elif pl_decision + en_decision == 'dodgeattack':
                    chance = rm.randint(0,1)
                    if chance:
                        text = 'Dodged'
                        p_dodged = True
                    else:
                        dmg_player()
                        text = 'Dodge unsuccessful'

                elif pl_decision + en_decision == 'attackdodge':
                    chance = rm.randint(0,1)
                    if chance:
                        text = 'Hit'
                        en_dodged = True
                    else:
                        dmg_enemy()
                        text = 'Missed'

                elif pl_decision + en_decision == 'attackblock' or pl_decision + en_decision == 'blockattack':
                    if pl_decision + en_decision == 'attackblock':
                        dmg_enemy(0.5)
                        dmg_player(0.5, True)
                    else:
                        dmg_enemy(0.5, True)
                        dmg_player(0.5)
                    text = 'Blocked'

        p.display.update()

        conflict = False
       
        for event in p.event.get():
            if event.type == QUIT:
                p.quit()
                sys.exit()

        if keys[p.K_q]:
            choice = 1
        if keys[p.K_w]:
            choice = 2
        if keys[p.K_e]:
            choice = 3
        if keys[p.K_r]:
            choice = 4

        choice = choice % 5
                
        if m.g.HP <= 0:
            timer_run = False
            time_elapsed = p.time.get_ticks()  - time_started
            battle_over = True
            gameover(2, time_elapsed)

        if m.en.HP <= 0:
            p.mixer.music.load('Factory.ogg')
            p.mixer.music.set_volume(0.09)
            p.mixer.music.play(-1)
            m.g.pts += rm.randrange(10,25)
            m.en.HP = rm.randrange(2,5)*m.g.lvl
            m.en.amr = rm.randrange(0,3)*m.g.lvl
            display.blit(loading, (0,0))
            loading_text = univ_font.render('Press any key to continue', True, white)
            display.blit(loading_text, (windowx/3 +43, windowy- 30))
            
            p.display.update()
            time.sleep(1)
            battle_over = True         

def dmg_enemy(mult = 1, self_dmg = False):
    if self_dmg:
        if m.en.amr > 0:
            m.en.amr -= int(m.en.dmg * mult)
            if m.en.amr < 0:
                a = m.en.amr
                m.en.HP += a
                m.en.amr = 0
        else:
            m.en.HP -= int(m.en.dmg * mult)

    else:
        if m.en.amr > 0:
            m.en.amr -= int(m.g.dmg * mult)
            if m.en.amr < 0:
                a = m.en.amr
                m.en.HP += a
                m.en.amr = 0
        else:
            m.en.HP -= int(m.g.dmg * mult)

def dmg_player(mult = 1, self_dmg = True):
    if self_dmg:
        if m.g.amr > 0:
            m.g.amr -= int(m.g.dmg * mult)
            if m.g.amr < 0:
                a = m.g.amr
                m.g.HP += a
                m.g.amr = 0
        else:
            m.g.HP -= int(m.g.dmg * mult)
    else:
        if m.g.amr > 0:
            m.g.amr -= int(m.en.dmg * mult)
            if m.g.amr < 0:
                a = m.g.amr
                m.g.HP += a
                m.g.amr = 0
        else:
            m.g.HP -= int(m.en.dmg * mult)

#function to make sprites and rects collide
#for wall collision to
def hbcollide(one,two):
    return one.hitbox.colliderect(two.rect)

#START_SCREEN PART
class Option:
    hovered = False

    def __init__(self, text, position, font):
        self.text = text
        self.position = position
        self.font = font
        self.set_rect()
        self.draw()

    def draw(self):
        self.set_rend()
        display.blit(self.rend, self.rect)

    def set_rend(self):
        self.rend = self.font.render(self.text, True, self.get_color())

    def get_color(self):
        if self.hovered:
            return white_light
        else:
            return GREEN

    def set_rect(self):
        self.set_rend()
        self.rect = self.rend.get_rect()
        self.rect.topleft = self.position

class Start_Screen:
    def __init__(self, bg_img): 
        self.bg_img = bg_img
        self.start_loop()

    def start_loop(self):
        exit_game = False
        start_screen = True
        menu_font = p.font.Font(None, 40)
        options = [Option("PLAY GAME", (150, 500), menu_font), Option("EXIT GAME", (450, 500), menu_font),
               Option("OPTIONS", (750, 500), menu_font)]
        bg = p.image.load(self.bg_img)
        while not exit_game and start_screen:
            display.blit(bg, (0,0)) #my name for the display is screen note that
            p.event.pump()
            for option in options:
                event = p.event.wait()
                if event.type == p.QUIT:
                    exit_game = True
                    p.quit()
                if option.rect.collidepoint(p.mouse.get_pos()):
                    option.hovered = True
                    event = p.event.wait()
                    if option == options[0] and event.type ==p.MOUSEBUTTONDOWN:
                        display.blit(loading, (0,0))
                        loading_text = univ_font.render('Press any key to continue', True, white)
                        display.blit(loading_text, (windowx/3 +43, windowy- 30))
                        p.display.update()
                        print('Start')
                        start_screen = False
                        return True
                    if option == options[1] and event.type ==p.MOUSEBUTTONDOWN:
                        print('Exit')
                        exit_game = True
                        p.quit()
                    if option == options[2] and event.type ==p.MOUSEBUTTONDOWN:
                        display.blit(loading, (0,0))
                        loading_text = univ_font.render('Press any key to continue', True, white)
                        display.blit(loading_text, (windowx/3 +43, windowy- 30))
                        p.display.update()
                        print('Options')
##                        p.mixer.Channel(0).play(p.mixer.Sound('click.mp3'))
                        time.sleep(1)
                        
                        Settings(BGSetting_IMG)
                else:
                    option.hovered = False
                option.draw()
            p.display.update()

class Settings:
    def __init__(self, bg_img):
        self.bg_img = bg_img
        self.settings_loop()

    def settings_loop(self):
        exit_game = False
        settings_screen = True
        menu_font = p.font.Font(None, 40)
        options = [Option('INSTRUCTIONS', (150, 200), menu_font), Option("LEADERBOARD", (450, 200), menu_font),
           Option("BACK TO MENU", (750, 200), menu_font)]
        bg = p.image.load(self.bg_img)
        while not exit_game and settings_screen:
            display.blit(bg, (0,0)) #note: my name for the display is screen 
            p.event.pump()
            for option in options:
                event = p.event.wait()
                if event.type == p.QUIT:
                    exit_game = True
                    p.quit()
                if option.rect.collidepoint(p.mouse.get_pos()):
                    option.hovered = True
                    if option == options[0] and event.type == p.MOUSEBUTTONDOWN:
                        settings_screen = False
                        Instructions(INSTRUCTIONS_BG)
                    if option == options[1] and event.type == p.MOUSEBUTTONDOWN:
                        settings_screen = False
                        Leaderboard(LEADERBOARD_BG, SCORES_FILE)
                    if option == options[2] and event.type == p.MOUSEBUTTONDOWN:
                        settings_screen = False
                        display.blit(loading, (0,0))
                        loading_text = univ_font.render('Press any key to continue', True, white)
                        display.blit(loading_text, (windowx/3 +43, windowy- 30))
                        p.display.update()
                        break
##                        Start_Screen(START_BG)
                else:
                    option.hovered = False
                option.draw()
            p.display.update()

class Instructions:
    def __init__(self, bg_img):
        self.bg_img = bg_img
        self.instructions_loop()

    def instructions_loop(self):
        exit_game = False
        instructions_screen = True
        menu_font = p.font.Font(None, 40)
        options = [Option("BACK TO MENU", (150, 580), menu_font)]
        bg = p.image.load(self.bg_img)
        while not exit_game and instructions_screen:
            display.blit(bg, (0,0)) #note: my name for the display is screen 
            p.event.pump()
            for option in options:
                event = p.event.wait()
                if event.type == p.QUIT:
                    exit_game = True
                    p.quit()
                if option.rect.collidepoint(p.mouse.get_pos()):
                    option.hovered = True
                    if option == options[0] and event.type == p.MOUSEBUTTONDOWN:
                        instructions_screen = False
                        display.blit(loading, (0,0))
                        loading_text = univ_font.render('Press any key to continue', True, white)
                        display.blit(loading_text, (windowx/3 +43, windowy- 30))
                        p.display.update()
                        break
##                        Start_Screen(START_BG)
                else:
                    option.hovered = False
                option.draw()
            p.display.update()

class Leaderboard():
    def __init__(self, bg_img, score_file):
        self.bg_img = bg_img
        self.score_file = score_file
        self.create_rank()
        self.score_loop()
            
    def create_rank(self):
        #open file, read write append mode
        with open(self.score_file) as fh:
            content = fh.read()
        lines = content.split('\n')
        while '' in lines:
            lines.remove('')

        score_list = []
        for line in lines:
            # NAME:TIME:SCORE
            score_stat = line.split('|')
            score_list.append(score_stat)

        ranked_list = sorted(score_list, key = lambda stat: int(stat[2]), reverse = True)
        
        #ten_rank
        top_ten = ranked_list[:10]
        
        #display_scores
        menu_font = p.font.Font(None, 30)
        bg = p.image.load(self.bg_img)
        display.blit(bg, (0,0))
        
        incr_y = 40
        y = 150
        dxdy_name = (100, y)
        dxdy_time = (400, y)
        dxdy_score = (800, y)
        for each in top_ten:
            name_text = menu_font.render(each[0], True, white)
            display.blit(name_text, dxdy_name)
            time_text = menu_font.render(each[1], True, white)
            display.blit(time_text, dxdy_time)
            score_text = menu_font.render(each[2], True, white)
            display.blit(score_text, dxdy_score)
            y += incr_y
            dxdy_name = (100, y)
            dxdy_time = (400, y)
            dxdy_score = (800, y)
        p.display.update()

        return top_ten

    def score_loop(self):
        exit_game = False
        score_screen = True
        
        menu_font = p.font.Font(None, 40)
        options = [Option("BACK TO MENU", (750, 550), menu_font)]
        while not exit_game and score_screen:
            p.event.pump()
            for option in options:
                event = p.event.wait()
                if event.type == p.QUIT:
                    exit_game = True
                    p.quit()
                if option.rect.collidepoint(p.mouse.get_pos()):
                    option.hovered = True
                    if option == options[0] and event.type == p.MOUSEBUTTONDOWN:
                        print('Menu')
                        score_screen = False
                        display.blit(loading, (0,0))
                        loading_text = univ_font.render('Press any key to continue', True, white)
                        display.blit(loading_text, (windowx/3 +43, windowy- 30))
                        p.display.update()
                        break
##                        Start_Screen(START_BG)
                else:
                    option.hovered = False
                option.draw()
            p.display.update()    

exit_game = False

while not exit_game:  
    allsprites = p.sprite.Group()
    allwalls = p.sprite.Group()
    allitems = p.sprite.Group()
    allexit = p.sprite.Group()
    allenemies = p.sprite.Group()

    lvl = 1
    #current_level = 1

    #calling Start_screen
    start_game = Start_Screen(START_BG)
    
    dead = False
    if start_game:
        m = maps(lvl)
        m.the_map()

        #timer part
        time_started = p.time.get_ticks()
        font  = p.font.Font(None, 40)

    while not dead and start_game:
        t.tick(fps)

        passed_time = p.time.get_ticks()  - time_started

        timer = convert_time(passed_time)
        display_time = font.render(timer, True, black)
        display.blit(display_time, (800, 0))
        p.display.update()
        
        for e in p.event.get():
            if e.type == QUIT or (e.type == KEYUP and e.key == K_ESCAPE):
                p.quit()
                sys.exit()
            elif e.type == KEYDOWN:
                if e.key == K_w:
                    m.g.a = -1
                if e.key == K_x:
                    m.g.a = 1
                if e.key == K_a:
                    if not m.g.turn_right:
                        m.g.turn_left = True
                    m.g.turn_right = False
                if e.key == K_d:
                    if not m.g.turn_left:
                        m.g.turn_right = True
                    m.g.turn_left = False
                if e.key == K_s:
                    m.g.move = 0
            elif e.type == KEYUP:
                if e.key == K_w:
                    m.g.a = 0
                if e.key == K_s:
                    m.g.a = 0
                if e.key == K_a:
                    m.g.turn_left = False
                if e.key == K_d:
                    m.g.turn_right = False
        m.g.move += m.g.a
        m.g.a = 0
        if m.g.move:
            m.g.dx = (-m.g.move*cos(m.g.orientation + (pi/2)))
            m.g.dy = (m.g.move*sin(m.g.orientation + (pi/2)))
        else:
            m.g.dx = 0
            m.g.dy = 0
        if m.g.turn_left:
            m.g.dz = pi/90
        elif m.g.turn_right:
            m.g.dz = -pi/90
        else:
            m.g.dz = 0
        m.g.orientation += m.g.dz
        m.g.posx += m.g.dx
        m.g.posy += m.g.dy
        m.g.hitbox.centerx = m.g.posx
        m.g.hitbox.centery = m.g.posy
        

        m.g.bump(allwalls, 'x')
        m.g.bump(allwalls, 'y')

        m.g.rect.center = m.g.hitbox.center

        if m.g.lvl > lvl:
            lvl = m.g.lvl
            if lvl <= 3:
                HP = m.g.HP
                dmg = m.g.dmg
                amr = m.g.amr
                pts = m.g.pts
                lvl = m.g.lvl
                allsprites = p.sprite.Group()
                allwalls = p.sprite.Group()
                allitems = p.sprite.Group()
                allexit = p.sprite.Group()
                allenemies = p.sprite.Group()
                m = maps(lvl)
                m.the_map()
            else:
                m.g.lvl = 1
                m.g.pts += 100
                start_game = False
                dead = True
                time_elapsed = p.time.get_ticks() - time_started
                gameover(1, time_elapsed)
        if m.g.HP <= 0 or dead or  not start_game:
            dead = True
        else:
            draw()
                
