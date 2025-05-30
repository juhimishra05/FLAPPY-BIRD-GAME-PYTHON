import pygame as pg 
import sys,time
from bird import Bird
from pipe import Pipe
from pygame import mixer 

pg.init()
mixer.init()

class Game:
    def __init__(self):
        # setting the window configurations
        self.width = 600 
        self.height = 768 
        self.scale_factor = 1.5
        self.win = pg.display.set_mode((self.width,self.height))
        self.clock = pg.time.Clock()
        self.move_speed = 200
        
        # Sfx
        self.flap_sound = mixer.Sound("assets/sfx/flap.wav")
        self.score_sound = mixer.Sound("assets/sfx/score.wav")
        self.dead_sound = mixer.Sound("assets/sfx/dead.wav")
        
        # Game Loop
        self.is_enter_pressed = False
        self.is_game_started = True
        
        # Bird  
        self.bird =Bird(self.scale_factor)

        self.font = pg.font.Font("assets/font.ttf",24)
        
        self.start_text = self.font.render("Press Enter to Play",True,(255,255,255))
        self.start_text_rect = self.start_text.get_rect(center=(300,300))
        
        self.score_text = self.font.render("Score: 0 ",True,(255,255,255))
        self.score_text_rect = self.score_text.get_rect(center=(100,30))
        
        self.restart_text = self.font.render("Restart",True,(255,255,255))
        self.restart_text_rect = self.restart_text.get_rect(center=(300,300))
        
        # Score
        self.start_monitoring = False       
        self.score = 0 
        
        # Pipes
        self.pipes = []
        self.pipe_generate_counter = 105
      
        self.setupBgAndGround()
        self.gameLoop()
    
    def gameLoop(self):
        last_time = time.time()
        while True:
            # Calculating Delta Time
            new_time = time.time()
            dt = new_time - last_time 
            last_time = new_time
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    pg.quit()
                    sys.exit()
                    break
            
                if event.type == pg.KEYDOWN and self.is_game_started:
                    # if enter pressed and game is started
                    if event.key == pg.K_RETURN:
                        self.is_enter_pressed = True
                        self.bird.is_not_collided = True
                     # if space pressed and game is running
                    elif event.key == pg.K_SPACE and self.is_enter_pressed:
                        self.flap_sound.play()
                        self.bird.flap(dt)
                # pressing restart rect
                if event.type == pg.MOUSEBUTTONDOWN:
                    if self.restart_text_rect.collidepoint(pg.mouse.get_pos()):
                        self.restartGame()
                        
            self.updateEverything(dt)
            self.checkCollisions()
            self.checkScore()
            self.drawEverything()
            pg.display.update()
            self.clock.tick(60)

    def checkScore(self):
        if len(self.pipes)>0:
            
            first_pipe = self.pipes[0].rect_down # rect down or rect up both works
            bird_left = self.bird.rect.left
            bird_right = self.bird.rect.right

            if (bird_left > first_pipe.left and bird_right < first_pipe.right and not self.start_monitoring):
                self.start_monitoring = True
            
            if bird_left > first_pipe.right and self.start_monitoring:
                self.start_monitoring = False
                self.score+=1
                self.score_sound.play()
                self.score_text = self.font.render(f"Score: {self.score}",True,(255,255,255))
               
    def checkCollisions(self):
        pipe_collision = False
        
        if len(self.pipes):
            # checking if bird collided with upper or lower pipe
            pipe_collision = self.bird.rect.colliderect(self.pipes[0].rect_down) or self.bird.rect.colliderect(self.pipes[0].rect_up)
        
        if pipe_collision:
            self.is_enter_pressed = False
            self.is_game_started = False
            self.dead_sound.play()
            
        if self.bird.rect.bottom > 568:
            self.bird.is_not_collided = False
            self.is_game_started = False
            self.dead_sound.play()
    
    def updateEverything(self,dt):
        if self.is_enter_pressed:
            # Moving the ground
            self.ground1_rect.x -= int(self.move_speed*dt)
            self.ground2_rect.x -= int(self.move_speed*dt)

            if self.ground1_rect.right<=0:
                self.ground1_rect.x = self.ground2_rect.right
            if self.ground2_rect.right<=0:
                self.ground2_rect.x = self.ground1_rect.right 
            # generating pipes
            if self.pipe_generate_counter>105:
                self.pipes.append(Pipe(self.scale_factor,self.move_speed))
                self.pipe_generate_counter = 0
                # print("pipe created")
            self.pipe_generate_counter+=1
            
            # moving the pipes
            for pipe in self.pipes:
                pipe.update(dt)
                
            # deleting the first pipe that got out of screen
            if len(self.pipes)!=0:
                if  self.pipes[0].rect_up.right<0:
                    self.pipes.pop(0)
                    # print("pipe removed")
  
        # moving the bird 
        self.bird.update(dt)
      
    def drawEverything(self):
      # blit method is used for showing something on screen buffer
      
        self.win.blit(self.bg_img,(0,-280))
        for pipe in self.pipes :
            pipe.drawPipe(self.win)
        self.win.blit(self.ground1_img,self.ground1_rect)
        self.win.blit(self.ground2_img,self.ground2_rect)
        self.win.blit(self.bird.image,self.bird.rect)
        self.win.blit(self.score_text,self.score_text_rect)
        
        if self.is_game_started and not self.is_enter_pressed:
            self.win.blit(self.start_text,self.start_text_rect)
        elif not self.is_game_started:  
            self.win.blit(self.restart_text,self.restart_text_rect)
    
    def restartGame(self):
        self.score = 0 
        self.score_text = self.font.render("Score: 0 ",True,(255,255,255))
        self.is_enter_pressed = False 
        self.is_game_started = True
        self.bird.resetPosition()
        self.pipes.clear()
        self.pipe_generate_counter = 105
        self.bird.is_not_collided = False    
        
    def setupBgAndGround(self):
        # Loading the basic background images
        self.bg_img = pg.transform.scale_by(pg.image.load("assets/bg.png").convert(),self.scale_factor) 
        self.ground1_img = pg.transform.scale_by(pg.image.load("assets/ground.png").convert(),self.scale_factor) 
        self.ground2_img = pg.transform.scale_by(pg.image.load("assets/ground.png").convert(),self.scale_factor) 
        
        self.ground1_rect = self.ground1_img.get_rect()
        self.ground2_rect = self.ground2_img.get_rect()
        
        self.ground1_rect.x = 0
        self.ground1_rect.y = 568
        self.ground2_rect.y = 568
        self.ground2_rect.x = self.ground1_rect.right
        
           
flappy = Game()