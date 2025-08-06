from superwires import games, color
from flask import Flask
import random, os, subprocess,pygame
app = Flask(__name__) 
app.run(host="0.0.0.0", port=10000)
@app.route('/')
# Get the root of the current Git repository
repo_root = subprocess.check_output(['git', 'rev-parse', '--show-toplevel']).decode().strip()

# Set XDG_RUNTIME_DIR to the GitHub repository root
os.environ["XDG_RUNTIME_DIR"] = repo_root
os.environ["SDL_AUDIODRIVER"] = "dummy"
games.init(screen_width = 1256, screen_height = 690, fps = 50)


class PlayerTank(games.Sprite):
    game_over = False
    level = 0
    enemies = 0
    power = 3
    timer = 0
    pow_time = 0
    #lev_sound = games.load_sound("level.wav")
    image = games.load_image("left_tank.bmp")

    power_display = games.Text(value = "Power: " + str(power),
                               size = 30,
                               color = color.black,
                               top = 40,
                               left = 10,
                               is_collideable = False)
    
    level_display = games.Text(value = level,
                       size = 30,
                       color = color.white,
                       top = 20,
                       right = games.screen.width - 50,
                       is_collideable = False)
    
    score = games.Text(value = level,
                       size = 30,
                       color = color.black,
                       top = 20,
                       left = 105,
                       is_collideable = False)
    

    
    def __init__(self):
        super(PlayerTank, self).__init__(image = PlayerTank.image,
                                         left = 0,
                                         y = games.screen.height - 50)
        games.screen.add(PlayerTank.level_display)
        games.screen.add(PlayerTank.score)
        games.screen.add(PlayerTank.power_display)
        
       
        
    def update(self):
        
        PlayerTank.timer -= 1
        PlayerTank.pow_time -= 1
        if self.left < 0:
            self.left = 0
        if self.right > 400:
            self.right = 400
            #move tank left
        if games.keyboard.is_pressed(games.K_LEFT):
            self.x -= 5
            #move tank right
        if games.keyboard.is_pressed(games.K_RIGHT):
            self.x += 5
            #fire weapon
        if games.keyboard.is_pressed(games.K_SPACE) and PlayerTank.timer < 0:            
           # new_bullet = Bullet(self.x + 20, self.y - 20, self.power)
            new_bullet = Bullet(self.right + 10, self.top - 10, PlayerTank.power, side = 'good')
            games.screen.add(new_bullet)
            PlayerTank.timer = 20
            #increase firepower
        if games.keyboard.is_pressed(games.K_UP) and PlayerTank.pow_time <= 0:
            if PlayerTank.power < 9:
                PlayerTank.power += 1
                PlayerTank.power_display.value = "Power: " + str(PlayerTank.power)
                PlayerTank.pow_time = 10
            #decrease firepower
        if games.keyboard.is_pressed(games.K_DOWN) and PlayerTank.pow_time <= 0:
            if PlayerTank.power > 3:
                PlayerTank.power -= 1
                PlayerTank.power_display.value = "Power: " + str(PlayerTank.power)
                PlayerTank.pow_time = 10

        self.check_hit()
        self.check_next_level()

    def check_next_level(self):
        
        if PlayerTank.enemies <= 0:
            #bg = backgounds list index [level + 1
            #set bg as background]
            #new background for each level...
            #infinite levels though...
            PlayerTank.level += 1
            self.level_display.value += 1
            self.level_display.right = games.screen.width - 50
            #PlayerTank.lev_sound.play()
            for i in range(PlayerTank.level):
                enemy = EnemyTank(x = random.randrange(games.screen.width - 350, games.screen.width - 50),
                                  y = random.randrange(games.screen.height - 100, games.screen.height - 25), side = 'bad')
                PlayerTank.enemies += 1
                games.screen.add(enemy)
            if PlayerTank.level == 2:
                new_bg = games.load_image("bg.jpg", transparent = False)
                games.screen.background = new_bg
            if PlayerTank.level == 3:
                new_bg = games.load_image("bg3.jpg", transparent  = False)
                games.screen.background = new_bg
            
            
    def check_hit(self):
        if self.overlapping_sprites:
            for sprite in self.overlapping_sprites:
                sprite.die()
                self.die()
    

    def die(self):
        PlayerTank.game_over = True
        self.destroy()
        new_explosion = Explosion(self.x, self.y)
        games.screen.add(new_explosion)
        end_message = games.Message(value = "Game Over",
                                    size = 90, color = color.red,
                                    x = games.screen.width/2,
                                    y = games.screen.height/2,
                                    lifetime = 3*games.screen.fps,
                                    after_death = games.screen.quit,
                                    is_collideable = False)
        games.screen.add(end_message)

class EnemyTank(games.Sprite):
    image = games.load_image("right_tank.bmp")
    

    def __init__(self, x, y, speed = 2, movement_range = 100, side = 'bad'):
        super(EnemyTank, self).__init__(image = EnemyTank.image,
                                        x = x, y = y,
                                        dx = -speed*0.75)
        self.movement = movement_range
        self.speed = speed
        self.time_til_shot = 0
        self.side = side
        

    def update(self):
        if self.right > games.screen.width or self.left < games.screen.width - 400:
            self.dx = -self.dx
        if random.randrange(self.movement) == 14:
            self.dx = -self.dx
        if self.left < games.screen.width - 400:
            self.left = games.screen.width - 400
        if self.right > games.screen.width:
            self.right = games.screen.width
        self.check_hit()
        self.check_fire()

    def check_hit(self):
        if self.overlapping_sprites:
            for sprite in self.overlapping_sprites:
                if type(sprite).__name__ != 'EnemyTank' and sprite.side != 'bad':
                    sprite.die()
                    self.die()

    def check_fire(self):
        if self.time_til_shot > 0:
            self.time_til_shot -= 1
        else:
            enemy_bullet = Bullet(x = self.left + 10, y = self.top - 10, dx = random.randrange(-5, -2), side = "bad")
            games.screen.add(enemy_bullet)
            self.time_til_shot = 60
            
    
    def die(self):
        PlayerTank.enemies -= 1
        if PlayerTank.game_over == False:
            PlayerTank.score.value += 100*PlayerTank.level
        PlayerTank.score.left = 105
        self.destroy()
        new_explosion = Explosion(self.x, self.y)
        games.screen.add(new_explosion)

class Explosion(games.Animation):
    """Explosion animation"""
    #sound = games.load_sound("explosion.wav")
    images = []
    for i in os.listdir(os.getcwd()):
        if "explosion" in i and ".bmp" in i:
            images.append(i)
    def __init__(self, x = games.screen.width/2, y = games.screen.height/2):
        super(Explosion, self).__init__(images = Explosion.images,
                                        x = x, y = y,
                                        repeat_interval = 4,
                                        n_repeats = 1, is_collideable = False)
        #Explosion.sound.play()


class Bullet(games.Sprite):
    image = games.load_image("missile.bmp")
    #sound = games.load_sound("missile.wav")
    time = 0.0

    def __init__(self, x, y, dx, side):
        super(Bullet, self).__init__(image = Bullet.image, x = x, y = y, dx = dx)
        #Bullet.sound.play()

        self.side = side

    def update(self):
        self.time += 0.02
        self.y -= (10*self.time - 0.5*9.81*self.time**2)

        if self.x < 0 or self.x > games.screen.width or self.y > games.screen.height:
            self.die()
    

    def die(self):
        self.destroy()
        if PlayerTank.game_over == False:
            PlayerTank.score.value += 10
        PlayerTank.score.left = 105
        new_explosion = Explosion(self.x, self.y)
        games.screen.add(new_explosion)

class instructions(games.Sprite):
    image = games.load_image("instructions.bmp", transparent = False)
    def __init__(self, x = games.screen.width/2, y = games.screen.height/2):
        super(instructions, self).__init__(image = instructions.image, x = x, y = y)
        
    def update(self):
        if games.keyboard.is_pressed(games.K_SPACE):
            self.destroy()
            main()
        
def main():
    
    #games.music.load("themey.mp3")
    #games.music.play(-1)
    background_image = games.load_image("barbedbg.jpg", transparent = False)
    games.screen.background = background_image
    player = PlayerTank()
    
    games.screen.add(player)
    games.screen.event_grab = True
    games.mouse.is_visible = False


instructions = instructions()
games.screen.add(instructions)
games.screen.mainloop()














