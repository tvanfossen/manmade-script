import pygame, random
from pygame.locals import *

class PongGame:
    def __init__(self, task_q, bio_q_algo, condition, type):
        self.type = type
        self.start_game(task_q, condition, bio_q_algo)


    def start_game(self, task_q, condition, bio_q_algo):
        self.bio_q_algo = bio_q_algo
        self.condition = condition

        # Number of frames per second
        # Change this value to speed up or slow down your game
        FPS = 200

        #Global Variables to be used through our program

        WINDOWWIDTH = 800
        WINDOWHEIGHT = 500
        LINETHICKNESS = 10
        PADDLESIZE = 50
        PADDLEOFFSET = 20

        # Set up the colours
        BLACK     = (0  ,0  ,0  )
        WHITE     = (255,255,255)

        pygame.init()
        global DISPLAYSURF
        ##Font information
        global BASICFONT, BASICFONTSIZE
        BASICFONTSIZE = 20
        BASICFONT = pygame.font.Font('freesansbold.ttf', BASICFONTSIZE)

        pygame.font.init()

        font = pygame.font.SysFont('Consolas', 48)

        FPSCLOCK = pygame.time.Clock()

        DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH,WINDOWHEIGHT), pygame.FULLSCREEN)
        # DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))

        pygame.display.set_caption('Pong')

        # Initiate variable and set starting positions
        # any future changes made within rectangles
        ballX = WINDOWWIDTH / 2 - LINETHICKNESS / 2
        ballY = WINDOWHEIGHT / 2 - LINETHICKNESS / 2
        playerOnePosition = (WINDOWHEIGHT - PADDLESIZE) / 2
        playerTwoPosition = (WINDOWHEIGHT - PADDLESIZE) / 2
        score = 0

        # Keeps track of ball direction
        ballDirX = -1  ## -1 = left 1 = right
        ballDirY = -1  ## -1 = up 1 = down

        # Creates Rectangles for ball and paddles.
        paddle1 = pygame.Rect(PADDLEOFFSET, playerOnePosition, LINETHICKNESS + 10, PADDLESIZE + 10)
        paddle2 = pygame.Rect(WINDOWWIDTH - PADDLEOFFSET - LINETHICKNESS, playerTwoPosition, LINETHICKNESS + 10,
                              PADDLESIZE + 10)
        ball = pygame.Rect(ballX, ballY, LINETHICKNESS, LINETHICKNESS)

        # Draws the starting position of the Arena

        pygame.mouse.set_visible(0)  # make cursor invisible

        #Draws the arena the game will be played in.
        def drawArena():
            pygame.display.init()
            DISPLAYSURF.fill((75,75,75))
            #Draw outline of arena
            pygame.draw.rect(DISPLAYSURF, WHITE, ((0,0),(WINDOWWIDTH,WINDOWHEIGHT)), LINETHICKNESS*2)
            #Draw centre line
            # pygame.draw.line(DISPLAYSURF, WHITE, ((WINDOWWIDTH/2),0),((WINDOWWIDTH/2),WINDOWHEIGHT), (LINETHICKNESS/4))

        #Draws the paddle
        def drawPaddle(paddle):
            #Stops paddle moving too low
            if paddle.bottom > WINDOWHEIGHT - LINETHICKNESS:
                paddle.bottom = WINDOWHEIGHT - LINETHICKNESS
            #Stops paddle moving too high
            elif paddle.top < LINETHICKNESS:
                paddle.top = LINETHICKNESS
            #Draws paddle
            pygame.draw.rect(DISPLAYSURF, WHITE, paddle)

        #draws the ball
        def drawBall(ball):
            pygame.draw.circle(DISPLAYSURF, WHITE, (ball.x, ball.y), 8, 0)

        #moves the ball returns new position
        def moveBall(ball, ballDirX, ballDirY):
            ball.x += ballDirX
            ball.y += ballDirY
            return ball

        #Checks for a collision with a wall, and 'bounces' ball off it.
        #Returns new direction
        def checkEdgeCollision(ball, ballDirX, ballDirY):
            if ball.top == (LINETHICKNESS) or ball.bottom == (WINDOWHEIGHT - LINETHICKNESS):
                ballDirY = ballDirY * -1
            if ball.left == (LINETHICKNESS) or ball.right == (WINDOWWIDTH - LINETHICKNESS):
                ballDirX = ballDirX * -1
            return ballDirX, ballDirY

        #Checks is the ball has hit a paddle, and 'bounces' ball off it.
        def checkHitBall(ball, paddle1, paddle2, ballDirX):
            if ballDirX == -1 and paddle1.right == ball.left and paddle1.top < ball.top and paddle1.bottom > ball.bottom:
                return -1
            elif ballDirX == 1 and paddle2.left == ball.right and paddle2.top < ball.top and paddle2.bottom > ball.bottom:
                return -1
            else: return 1

        #Checks to see if a point has been scored returns new score
        def checkPointScored(paddle1, ball, score, ballDirX):
            #reset points if left wall is hit
            if ball.left == LINETHICKNESS:
                return 0
            #1 point for hitting the ball
            elif ballDirX == -1 and paddle1.right == ball.left and paddle1.top < ball.top and paddle1.bottom > ball.bottom:
                score += 1
                return score
            #5 points for beating the other paddle
            elif ball.right == WINDOWWIDTH - LINETHICKNESS:
                score += 5
                return score
            #if no points scored, return score unchanged
            else: return score

        #Artificial Intelligence of computer player
        def artificialIntelligence(ball, ballDirX, paddle2):
            #If ball is moving away from paddle, center bat
            if ballDirX == -1:
                if paddle2.centery < (WINDOWHEIGHT/2):
                    paddle2.y += 1
                elif paddle2.centery > (WINDOWHEIGHT/2):
                    paddle2.y -= 1
            #if ball moving towards bat, track its movement.
            elif ballDirX == 1:
                if paddle2.centery < ball.centery:
                    paddle2.y += 1
                else:
                    paddle2.y -=1
            return paddle2

        #Displays the current score on the screen
        def displayScore(score):
            resultSurf = BASICFONT.render('Score = %s' %(score), True, WHITE)
            resultRect = resultSurf.get_rect()
            resultRect.topleft = (WINDOWWIDTH - 150, 25)
            DISPLAYSURF.blit(resultSurf, resultRect)

        def playBeat():
            print("PLAYING BEAT")
            self.beat.play()

        def adjustRate():
            print("ADJUSTING RATE")

            if self.play_rate < self.goal_rate:
                self.play_rate += self.increase_per_second

        def updateBiometrics():
            print ("BIOMETRICS")

            if self.bio_q_algo.qsize() > 1:
                temp = self.bio_q_algo.get_nowait()

                if temp is not None:
                    self.curHR = temp['HR']
                    self.curRR = temp['RR']

                    if int(self.curHR) > 90 or int(self.curHR) < 70:
                        self.threshold_counter += 1
                    else:
                        self.threshold_counter = 0

                    if self.threshold_counter > 10:
                        self.threshold_counter = 0
                        self.play_rate = 1 / (110 / 80)
                        self.increase_per_second = (self.goal_rate - self.play_rate) / (10 / self.play_rate)
                        # pygame.time.set_timer(pygame.USEREVENT + 4, self.play_rate * 1000)

        #Main function

        done = False
        start = True

        self.adjust_rate_flag = True
        self.threshold_counter = 0
        self.play_rate = 1 / (80/60)
        self.goal_rate = 1 / (80/60)
        self.increase_per_second = (self.goal_rate - self.play_rate) / 10

        self.curHR = -1
        self.curRR = -1

        self.beat = pygame.mixer.Sound("soundscapes/4_BRODY_SONIC_JOURNEY_v2_SINGLE_BEAT_DYNAMIC.ogg")
        self.beat.set_volume(0.10)
        self.end_counter = 0
        self.beat_counter = 0
        self.adjust_counter = 0
        self.biometrics_counter = 0
        self.log_counter = 0

        self.flag = False
        drawArena()
        drawPaddle(paddle1)
        drawPaddle(paddle2)
        drawBall(ball)

        self.ball = 'START'

        pygame.time.set_timer(pygame.USEREVENT+1, 50)

        # pygame.time.set_timer(pygame.USEREVENT+2, 100)
        #
        # pygame.time.set_timer(pygame.USEREVENT + 3, int(self.play_rate * 1000))
        # pygame.time.set_timer(pygame.USEREVENT + 4, 1000)
        # pygame.time.set_timer(pygame.USEREVENT + 5, 250)


        while not done: #main game loop
            if not start:

                drawArena()
                drawPaddle(paddle1)
                drawPaddle(paddle2)
                drawBall(ball)

                ball = moveBall(ball, ballDirX, ballDirY)
                ballDirX, ballDirY = checkEdgeCollision(ball, ballDirX, ballDirY)
                score = checkPointScored(paddle1, ball, score, ballDirX)
                ballDirX = ballDirX * checkHitBall(ball, paddle1, paddle2, ballDirX)
                paddle2 = artificialIntelligence(ball, ballDirX, paddle2)


                if checkHitBall(ball, paddle1, paddle2, ballDirX) == -1 and ballDirX == 1:
                    print("HIT")
                    self.ball = 'HIT'
                    self.flag = True
                elif ball.left == (LINETHICKNESS):
                    print("MISS")
                    self.ball = 'MISS'
                    self.flag = True
                elif not self.flag:
                    self.ball = 'TRAVELLING'

                displayScore(score)

                pygame.display.flip()
                FPSCLOCK.tick(FPS)

                for event in pygame.event.get():
                    if event.type == MOUSEMOTION:
                        mousex, mousey = event.pos
                        paddle1.y = mousey

                    elif event.type == pygame.USEREVENT + 1:
                        print(self.end_counter)
                        self.end_counter += 1
                        self.beat_counter += 1
                        self.adjust_counter += 1
                        self.biometrics_counter += 1
                        self.log_counter += 1

                        if self.type == 'experiment':
                            if self.end_counter > 20 * 300:
                                done = True
                                break
                        elif self.type == 'trial':
                            if self.end_counter > 20 * 60:
                                done = True
                                break
                        if self.log_counter > 20 * .1 and self.type == 'experiment':
                            self.log_counter = 0
                            self.flag = False
                            task_q.put({'task_name': 'session_pong',
                                        'metrics': {1: self.ball, 2: score, 3: -1, 4: -1, 5: -1, 6: -1, 7: -1}})

                        if self.condition == 4 and self.type == 'experiment':
                            if self.beat_counter > 20 * self.play_rate:
                                self.beat_counter = 0
                                playBeat()
                            if self.adjust_counter > 20 * self.play_rate:
                                self.adjust_counter = 0
                                adjustRate()
                            if self.biometrics_counter > 20 * .25:
                                self.biometrics_counter = 0
                                updateBiometrics()

                    elif event.type == QUIT:
                        pygame.display.quit()
                        pygame.quit()

                    elif event.type == KEYUP:
                        if event.key == K_ESCAPE:
                            done = True
                            break
            else:
                start = False

                # for event in pygame.event.get():  # event handling loop
                #     if event.type == KEYUP:
                #         if event.key == K_ESCAPE:
                #             done = True
                #             break
                #     elif event.type == pygame.USEREVENT:
                #         counter -= 1df
                #         if counter > 0:
                #             text = str(counter).rjust(3)
                #         else:
                #             text = "Start!"
                #             start = False
                #             DISPLAYSURF.fill((0, 0, 0))
                #             break
                #     elif event.type == QUIT:
                #         done = True
                #         break
                # else:
                #     DISPLAYSURF.fill((0, 0, 0))
                #     DISPLAYSURF.blit(font.render(text, True, (255, 255, 255)), (1920 / 2, 1080 / 2))
                #     pygame.display.flip()

        pygame.display.quit()


class WisconsinCardSort:
    def __init__(self, task_q, bio_q_algo, condition, number, init_rule, type):
        self.type = type
        self.bio_q_algo = bio_q_algo
        self.condition = condition
        self.type = type

        if init_rule == 'experiment':
            self.rules = ['color', 'shape', 'number']

            self.start_wcst(task_q, number, self.rules[random.randint(0,2)])
        else:
            self.start_wcst(task_q, number, init_rule)

    def start_wcst(self, task_q, number, init_rule):

        abs_path = "/home/tvanfossen/PycharmProjects/ManMadeMusic/assets/WCST/"

        pygame.init()
        screen = pygame.display.set_mode((1920, 1080), pygame.FULLSCREEN)
        # screen = pygame.display.set_mode((1920, 1080))


        pygame.font.init()


        font = pygame.font.SysFont('Consolas', 48)

        pygame.display.set_caption("WCST")
        done = False
        selection = True

        SCREEN_WIDTH = 1920
        SCREEN_HEIGHT = 1080

        colors = {1: 'red', 2: 'blue', 3: 'yellow', 4: 'green'}
        shapes = {1: 'tri', 2: 'square', 3: 'dot', 4: 'cross'}

        self.rules = ['color', 'shape', 'number']
        sort_rule = init_rule

        sorted = 0

        one_pos = Rect(SCREEN_WIDTH / 5 - 70, SCREEN_HEIGHT / 3, 140, 200)
        two_pos = Rect(SCREEN_WIDTH * 2 / 5 - 70, SCREEN_HEIGHT / 3, 140, 200)
        three_pos = Rect(SCREEN_WIDTH * 3 / 5 - 70, SCREEN_HEIGHT / 3, 140, 200)
        four_pos = Rect(SCREEN_WIDTH * 4 / 5 - 70, SCREEN_HEIGHT / 3, 140, 200)
        sort_pos = Rect(SCREEN_WIDTH / 2 - 70, SCREEN_HEIGHT * 2 / 3, 140, 200)
        result_pos = Rect(SCREEN_WIDTH/2 - 70, SCREEN_HEIGHT * 2 / 3 + 200, 70, 30 )
        card_pos = {1: one_pos, 2: two_pos, 3: three_pos, 4: four_pos}

        # clock = pygame.time.Clock()

        def blip_answer(result):
            print(result)
            text = result

            if result == 'correct':

                # right_image = pygame.image.load("/home/tvanfossen/PycharmProjects/ManMadeMusic/assets/WCST/right.png")
                # transition_image = pygame.image.load("/home/tvanfossen/PycharmProjects/ManMadeMusic/assets/WCST/right_transparent.png")
                for i in range (0,5):
                    screen.blit(font.render(text, True, (0, 255, 0)), (1920 / 2 - 70, SCREEN_HEIGHT * 2 / 3 - 70))
                    # screen.blit (right_image, result_pos)
                    pygame.display.flip()
                    pygame.time.delay(2)

                    screen.blit(font.render(text, True, (0, 200, 0)), (1920 / 2 - 70, SCREEN_HEIGHT * 2 / 3 - 70))
                    # screen.blit(transition_image, result_pos)
                    pygame.display.flip()
                    pygame.time.delay(2)

            else:
                # wrong_image = pygame.image.load("/home/tvanfossen/PycharmProjects/ManMadeMusic/assets/WCST/wrong.png")
                # transition_image = pygame.image.load("/home/tvanfossen/PycharmProjects/ManMadeMusic/assets/WCST/wrong_transparent.png")
                for i in range (0,5):
                    screen.blit(font.render(text, True, (255, 0, 0)), (1920 / 2 - 70, SCREEN_HEIGHT * 2 / 3 - 70))
                    # screen.blit (wrong_image, result_pos)
                    pygame.display.flip()
                    pygame.time.delay(2)

                    screen.blit(font.render(text, True, (200, 0, 0)), (1920 / 2 - 70, SCREEN_HEIGHT * 2 / 3 - 70))
                    # screen.blit(transition_image, result_pos)
                    pygame.display.flip()
                    pygame.time.delay(2)

            bg = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            bg.fill((0, 0, 0))
            screen.blit(bg, Rect(0,0,SCREEN_WIDTH, SCREEN_HEIGHT))
            pygame.display.flip()

        def restore_default():
            colors[1] = 'red'
            colors[2] = 'blue'
            colors[3] = 'yellow'
            colors[4] = 'green'

            shapes[1] = 'tri'
            shapes[2] = 'square'
            shapes[3] = 'dot'
            shapes[4] = 'cross'

        def randomize_cards():
            card_list = {}
            i = 1

            cor_color = None
            cor_shape = None

            sort_color = random.randint(1, 4)
            sort_shape = random.randint(1, 4)
            sort_number = random.randint(1, 4)

            card_list['sort'] = get_image(colors[sort_color], shapes[sort_shape], sort_number)

            while i <= 4:
                color = random.randint(1, 4)
                shape = random.randint(1, 4)
                number = i

                if color in colors and shape in shapes:
                    temp = get_image(colors[color], shapes[shape], number)
                    card_list[number] = temp
                    colors.pop(color)
                    shapes.pop(shape)
                    i += 1
                    if sort_rule == 'color' and color == sort_color:
                        cor_color = number
                    if sort_rule == 'shape' and shape == sort_shape:
                        cor_shape = number

                else:
                    continue

            restore_default()
            if sort_rule == 'number':
                return card_list, sort_number
            elif sort_rule == 'color':
                return card_list, cor_color
            else:
                return card_list, cor_shape

        def get_image(color, shape, number):
            return pygame.image.load(abs_path + color + '/' + color + str(number) + shape + '.png')

        def playBeat():
            print("PLAYING BEAT")
            self.beat.play()

        def adjustRate():
            print("ADJUSTING RATE")

            if self.play_rate < self.goal_rate:
                self.play_rate += self.increase_per_second

        def updateBiometrics():
            print ("BIOMETRICS")

            if self.bio_q_algo.qsize() > 1:
                temp = self.bio_q_algo.get_nowait()

                if temp is not None:
                    self.curHR = temp['HR']
                    self.curRR = temp['RR']

                    if int(self.curHR) > 90 or int(self.curHR) < 70:
                        self.threshold_counter += 1
                    else:
                        self.threshold_counter = 0

                    if self.threshold_counter > 10:
                        self.threshold_counter = 0
                        self.play_rate = 1 / (110 / 80)
                        self.increase_per_second = (self.goal_rate - self.play_rate) / (10 / self.play_rate)
                        # pygame.time.set_timer(pygame.USEREVENT + 4, self.play_rate * 1000)

        start = True

        self.new_cards = True

        self.play_rate = 1 / (80 / 60)
        self.goal_rate = 1 / (80 / 60)
        self.increase_per_second = (self.goal_rate - self.play_rate) / 10

        self.curHR = -1
        self.curRR = -1

        # pygame.time.set_timer(pygame.USEREVENT + 3, int(self.play_rate * 1000))
        # pygame.time.set_timer(pygame.USEREVENT + 4, 1000)
        # pygame.time.set_timer(pygame.USEREVENT + 5, 250)

        self.beat = pygame.mixer.Sound("soundscapes/4_BRODY_SONIC_JOURNEY_v2_SINGLE_BEAT_DYNAMIC.ogg")
        self.beat.set_volume(0.10)

        self.threshold_counter = 0
        self.end_counter = 0
        self.card_change_counter = 0
        self.beat_counter = 0
        self.adjust_counter = 0
        self.biometrics_counter = 0

        pygame.time.set_timer(pygame.USEREVENT + 1, 50)

        while not done:
            if not start:
                if selection:
                    cards, sort_val = randomize_cards()
                    print(sort_val)

                    screen.blit(cards[1], one_pos)
                    screen.blit(cards[2], two_pos)
                    screen.blit(cards[3], three_pos)
                    screen.blit(cards[4], four_pos)
                    screen.blit(cards['sort'], sort_pos)

                    pygame.time.delay(40)

                    selection = False

                for event in pygame.event.get():  # event handling loop
                    if event.type == MOUSEBUTTONUP:
                        if card_pos[sort_val].collidepoint(event.pos):
                            blip_answer("correct")
                            sorted += 1
                            selection = True
                            # STATUS / USER INPUT / CORRECT INPUT
                            if self.type == 'experiment':
                                task_q.put({'task_name': 'session_wcst',
                                            'metrics': {1: 'CORRECT', 2: sort_rule, 3: -1, 4: -1, 5: -1, 6: -1, 7: -1}})

                        else:
                            for i in card_pos:
                                if i != sort_val:
                                    if card_pos[i].collidepoint(event.pos):
                                        blip_answer("incorrect")
                                        selection = True
                                        sorted += 1
                                        # STATUS / USER INPUT / CORRECT INPUT
                                        if self.type == 'experiment':
                                            task_q.put({'task_name': 'session_wcst',
                                                        'metrics': {1: 'INCORRECT', 2: sort_rule, 3: -1, 4: -1, 5: -1,
                                                                    6: -1, 7: -1}})

                    elif event.type == pygame.USEREVENT + 1:
                        print(self.end_counter)

                        self.end_counter += 1
                        self.card_change_counter += 1
                        self.beat_counter += 1
                        self.adjust_counter += 1
                        self.biometrics_counter += 1

                        if self.end_counter > 20 * 300:
                            print("END")
                            done = True
                            break

                        if self.card_change_counter > 20 * 60:
                            print("CHANGE RULE")
                            self.card_change_counter = 0
                            temp = sort_rule
                            while temp == sort_rule:
                                temp = self.rules[random.randint(0, 2)]
                            sort_rule = temp

                        if self.condition == 4:
                            if self.beat_counter > 20 * self.play_rate:
                                self.beat_counter = 0
                                playBeat()
                            if self.adjust_counter > 20 * self.play_rate:
                                self.adjust_counter = 0
                                adjustRate()
                            if self.biometrics_counter > 20 * .25:
                                self.biometrics_counter = 0
                                updateBiometrics()

                    # elif event.type == pygame.USEREVENT+3 and self.condition == 4 and self.type == 'experiment':
                    #     playBeat()
                    #     pygame.time.set_timer(pygame.USEREVENT+3, int(self.play_rate*1000))
                    # elif event.type == pygame.USEREVENT+4 and self.condition == 4 and self.type == 'experiment':
                    #     adjustRate()
                    # elif event.type == pygame.USEREVENT+5 and self.condition == 4 and self.type == 'experiment':
                    #     updateBiometrics()

                    elif event.type == KEYUP:
                        if event.key == K_ESCAPE:
                            done = True
                            break
                    elif event.type == QUIT:
                        done = True
                        break



                if sorted == number:
                    done = True
                    break

            else:
                start = False
                # for event in pygame.event.get():  # event handling loop
                #     if event.type == KEYUP:
                #         if event.key == K_ESCAPE:
                #             done = True
                #             break
                #     elif event.type == pygame.USEREVENT:
                #         counter -= 1
                #         if counter > 0:
                #             text = str(counter).rjust(3)
                #         else:
                #             text = "Start!"
                #             start = False
                #             screen.fill((0,0,0))
                #             break
                #     elif event.type == QUIT:
                #         done = True
                #         break
                # else:
                #     screen.fill((0, 0, 0))
                #     screen.blit(font.render(text, True, (255, 255, 255)), (1920/2, 1080/2))
                #     pygame.display.flip()
                #     continue

            # clock.tick(60)
            pygame.display.flip()

        pygame.display.quit()


class DrivingGame:
    def __init__(self, task_q, bio_q_algo, condition, type):
        self.bio_q_algo = bio_q_algo
        self.condition = condition
        self.type = type
        self.start_driving(task_q, type)


    def start_driving(self, task_q, type):
        print("starting to drive")

        SCREEN_WIDTH = 1920
        SCREEN_HEIGHT = 1080
        LINE_HEIGHT = 10
        ROAD_LIMIT = 300

        pygame.display.init()
        pygame.init()

        pygame.font.init()

        clock = pygame.time.Clock()
        counter, text = 3, '3'.rjust(3)
        # pygame.time.set_timer(pygame.USEREVENT, 1000)
        font = pygame.font.SysFont('Consolas', 48)
        #
        # screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        # bg = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        #
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
        bg = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
        pygame.display.set_caption('Driving Game')

        done = False

        def init():
            temp_right = pygame.image.load("/home/tvanfossen/PycharmProjects/ManMadeMusic/assets/racing/road_line_xtrawide_right.png")
            temp_left = pygame.image.load("/home/tvanfossen/PycharmProjects/ManMadeMusic/assets/racing/road_line_xtrawide_left.png")
            temp_pos = {}
            temp_mid = 0

            for i in range (0, int(SCREEN_HEIGHT/LINE_HEIGHT)):
                temp_pos[str(i)+'right'] = Rect(SCREEN_WIDTH / 2, SCREEN_HEIGHT - LINE_HEIGHT * i, 1000, LINE_HEIGHT)
                temp_pos[str(i)+'right'].centerx = SCREEN_WIDTH / 2 + 500 + 125
                temp_pos[str(i) + 'left'] = Rect(SCREEN_WIDTH / 2 , SCREEN_HEIGHT - LINE_HEIGHT * i, 1000, LINE_HEIGHT)
                temp_pos[str(i)+'left'].centerx = SCREEN_WIDTH / 2 - 500 - 125


                bg.blit(temp_right, temp_pos[str(i) + 'right'])
                bg.blit(temp_left, temp_pos[str(i) + 'left'])

            return temp_right, temp_left, temp_pos, temp_mid

        def road_movement(nroad_right, nroad_left, nroad_pos, nmidpoint, obstacles):
            # i = int(SCREEN_HEIGHT/LINE_HEIGHT)
            bg.fill((0,0,0)) # remove everything from screen

            # ROAD RANDOMIZATION FIX, LARGE TURNS
            # REMOVE OBSTACLES?
            # LANE DEVIATION CHANGES SPEED

            for i in range (-int(SCREEN_HEIGHT/LINE_HEIGHT)+1, 0): # start at 768
                nroad_pos[str(abs(i)) + 'left'].centerx = nroad_pos[str(abs(i)-1) + 'left'].centerx
                nroad_pos[str(abs(i)) + 'right'].centerx = nroad_pos[str(abs(i) - 1) + 'right'].centerx

                bg.blit(nroad_left, nroad_pos[str(abs(i)) + 'left'])
                bg.blit(nroad_right, nroad_pos[str(abs(i)) + 'right'])

            nmidpoint += self.increase_per_cycle

            if nmidpoint > 400: nmidpoint = 400
            elif nmidpoint < -400: nmidpoint = -400

            nroad_pos['0right'] = Rect(SCREEN_WIDTH / 2 + nmidpoint, 1080, 1000, LINE_HEIGHT)
            nroad_pos['0right'].centerx = SCREEN_WIDTH / 2 + 500 + 125 + nmidpoint

            nroad_pos['0left'] = Rect(SCREEN_WIDTH / 2 + nmidpoint, 1080, 1000, LINE_HEIGHT)
            nroad_pos['0left'].centerx = SCREEN_WIDTH / 2 - 500 - 125 + nmidpoint

            # for i in obstacles:
            #     if i[1].centery < 15:
            #         obstacles.remove(i)
            #     else:
            #         i[1].centery -= 15
            #
            #         bg.blit(i[0], i[1])

            return nroad_right, nroad_left, nroad_pos, nmidpoint

        def car_update(ncar_pos_change, nroad_pos, obstacles):
            car = pygame.image.load("/home/tvanfossen/PycharmProjects/ManMadeMusic/assets/racing/race_car.png")

            car_pos = Rect(SCREEN_WIDTH / 2 + ncar_pos_change, 50, 40, 60)

            for i in range(0, int(SCREEN_HEIGHT/LINE_HEIGHT)):
                if car_pos.colliderect(nroad_pos[str(i)+'left']):
                    print("collide left")
                    self.scroll_val = min (45, self.scroll_val+1)
                if car_pos.colliderect(nroad_pos[str(i)+'right']):
                    print("collide right")
                    self.scroll_val = min (45, self.scroll_val+1)

            for i in obstacles:
                if car_pos.colliderect(i[1]):
                    self.collision = True
                    print("collide box")
                    obstacles.remove(i)
                    self.scroll_val = 45

            bg.blit(car, car_pos)

        def generate_obstacle(nmidpoint, obstacles):
            obstacle = pygame.image.load("/home/tvanfossen/PycharmProjects/ManMadeMusic/assets/racing/obstacle.png")
            rand_pos = 0
            temp = random.randint(-1,1)

            if temp == 1:
                rand_pos = 65
            elif temp == -1:
                rand_pos = -65

            obstacle_pos = Rect(SCREEN_WIDTH/2 + nmidpoint + rand_pos, 1080, 40, 40)

            obstacles.append((obstacle, obstacle_pos))

            return obstacles

        def playBeat():
            print("PLAYING BEAT")
            self.beat.play()

        def adjustRate():
            print("ADJUSTING RATE")

            if self.play_rate < self.goal_rate:
                self.play_rate += self.increase_per_second

        def updateBiometrics():
            print("BIOMETRICS")

            if self.bio_q_algo.qsize() > 1:
                temp = self.bio_q_algo.get_nowait()

                if temp is not None:
                    self.curHR = temp['HR']
                    self.curRR = temp['RR']

                    if int(self.curHR) > 90 or int(self.curHR) < 70:
                        self.threshold_counter += 1
                    else:
                        self.threshold_counter = 0

                    if self.threshold_counter > 10:
                        self.threshold_counter = 0
                        self.play_rate = 1 / (110 / 80)
                        self.increase_per_second = (self.goal_rate - self.play_rate) / (10 / self.play_rate)
                        # pygame.time.set_timer(pygame.USEREVENT + 4, self.play_rate * 1000)

        self.scroll_val = 45

        road_right, road_left, road_pos, midpoint = init()
        obstacles = []
        car_update(0, road_pos, obstacles)
        car_pos_change = 0
        self.collision = False
        total_distance = 0

        self.increase_per_cycle = 0

        self.adjust_rate_flag = True
        self.threshold_counter = 0
        self.play_rate = 1 / (80 / 60)
        self.goal_rate = 1 / (80 / 60)
        self.increase_per_second = (self.goal_rate - self.play_rate) / 10

        self.curHR = -1
        self.curRR = -1

        self.beat = pygame.mixer.Sound("soundscapes/4_BRODY_SONIC_JOURNEY_v2_SINGLE_BEAT_DYNAMIC.ogg")
        self.beat.set_volume(0.10)

        self.end_counter = 0
        self.beat_counter = 0
        self.adjust_counter = 0
        self.biometrics_counter = 0
        self.log_counter = 0
        self.road_counter = 0

        start = True
        pygame.time.set_timer(pygame.USEREVENT + 1, 50)

        # pygame.time.set_timer(pygame.USEREVENT + 2, 100)
        #
        # pygame.time.set_timer(pygame.USEREVENT + 3, int(self.play_rate * 1000))
        # pygame.time.set_timer(pygame.USEREVENT + 4, 1000)
        # pygame.time.set_timer(pygame.USEREVENT + 5, 250)
        # pygame.time.set_timer(pygame.USEREVENT + 6, 250)

        while not done:
            if not start:

                left_x = road_pos[str(abs(int(SCREEN_HEIGHT/LINE_HEIGHT)) - 7) + 'left'].bottomright[0] - 500
                right_x = road_pos[str(abs(int(SCREEN_HEIGHT/LINE_HEIGHT)) - 7) + 'right'].bottomleft[0] - 500

                car_actual = car_pos_change + 500

                mid = left_x + 125

                deviation = (car_actual - mid) / 125

                self.scroll_val = min(max(1, self.scroll_val-5) + abs(deviation*5), 45)

                pygame.time.delay(int(self.scroll_val))

                total_distance += 45 / self.scroll_val

                road_right, road_left, road_pos, midpoint = road_movement(road_right, road_left, road_pos, midpoint, obstacles)

                car_update(car_pos_change, road_pos, obstacles)

                keys_pressed = pygame.key.get_pressed()

                if keys_pressed[K_LEFT]:
                    car_pos_change -= 7

                if keys_pressed[K_RIGHT]:
                    car_pos_change += 7

                for event in pygame.event.get():  # event handling loop
                    if event.type == pygame.USEREVENT + 1:
                        print(self.end_counter)
                        self.end_counter += 1
                        self.beat_counter += 1
                        self.adjust_counter += 1
                        self.biometrics_counter += 1
                        self.log_counter += 1
                        self.road_counter += 1

                        if self.type == 'experiment':
                            if self.end_counter > 20 * 300:
                                done = True
                                break
                        elif self.type == 'trial':
                            if self.end_counter > 20 * 60:
                                done = True
                                break
                        if self.log_counter > 20 * .1 and self.type == 'experiment':
                            self.log_counter = 0
                            task_q.put({'task_name': 'session_driving',
                                        'metrics': {1: mid, 2: car_actual, 3: deviation,
                                                    4: -1, 5: -1, 6: -1, 7: -1}})
                        if self.road_counter > 20 * 0.25:
                            self.road_counter = 0
                            if midpoint > 300:
                                self.increase_per_cycle = -1
                            elif midpoint < -300:
                                self.increase_per_cycle = 1
                            elif self.increase_per_cycle < -5:
                                self.increase_per_cycle = -5
                            elif self.increase_per_cycle > 5:
                                self.increase_per_cycle = 5
                            else:
                                self.increase_per_cycle += random.randint(-2, 2)

                        if self.condition == 4 and self.type == 'experiment':
                            if self.beat_counter > 20 * self.play_rate:
                                self.beat_counter = 0
                                playBeat()
                            if self.adjust_counter > 20 * self.play_rate:
                                self.adjust_counter = 0
                                adjustRate()
                            if self.biometrics_counter > 20 * .25:
                                self.biometrics_counter = 0
                                updateBiometrics()


                    elif event.type == KEYUP:
                        if event.key == K_ESCAPE:
                            done = True
                            break
                    elif event.type == QUIT:
                        done = True
                        break
                    # elif event.type == pygame.USEREVENT+3 and self.condition == 4 and type == 'experiment':
                    #     playBeat()
                    #     pygame.time.set_timer(pygame.USEREVENT+3, int(self.play_rate*1000))
                    # elif event.type == pygame.USEREVENT+4 and self.condition == 4 and type == 'experiment':
                    #     adjustRate()
                    # elif event.type == pygame.USEREVENT+5 and self.condition == 4 and type == 'experiment':
                    #     updateBiometrics()
                    # elif event.type == pygame.USEREVENT+6:
                    #     if midpoint > 300:
                    #         self.increase_per_cycle = -1
                    #     elif midpoint < -300:
                    #         self.increase_per_cycle = 1
                    #     elif self.increase_per_cycle < -5:
                    #         self.increase_per_cycle = -5
                    #     elif self.increase_per_cycle > 5:
                    #         self.increase_per_cycle = 5
                    #     else:
                    #         self.increase_per_cycle += random.randint(-2,2)
                    # elif event.type == pygame.USEREVENT:
                    #     pygame.time.set_timer(pygame.USEREVENT, int(2000 * (1+self.scroll_val/30)))
                    #     obstacles = generate_obstacle(midpoint, obstacles)
                    # elif event.type == pygame.USEREVENT + 1:
                    #     self.end_counter += 1
                    #     done = True
                    #     break
                    # elif event.type == pygame.USEREVENT + 2 and type == 'experiment':
                    #     # obstacle_y = 1080
                    #     # for i in obstacles:
                    #     #     if i[1].centery < 1080:
                    #     #         obstacle_y = i[1].centery
                    #     # SEND DATA EVERY 100 MS
                    #     # MIDPOINT / CAR_POS / DEVIATION FROM CENTER /
                    #     task_q.put({'task_name': 'session_driving',
                    #                 'metrics': {1: mid, 2: car_actual, 3: deviation,
                    #                             4: -1, 5: -1, 6: -1, 7: -1}})
                    #
                    #     if self.collision:
                    #         self.collision = not self.collision

            else:
                start = False

                # for event in pygame.event.get():  # event handling loop
                #     if event.type == KEYUP:
                #         if event.key == K_ESCAPE:
                #             done = True
                #             break
                #     elif event.type == pygame.USEREVENT:
                #         counter -= 1
                #         if counter > 0:
                #             text = str(counter).rjust(3)
                #         else:
                #             text = "Start!"
                #             start = False
                #             break
                #     elif event.type == QUIT:
                #         done = True
                #         break
                # else:
                #     screen.fill((0, 0, 0))
                #     screen.blit(font.render(text, True, (255, 255, 255)), (1920/2, 1080/2))
                #     pygame.display.flip()
                #     continue

            screen.blit(font.render("Current Speed: " + str(int(45 / self.scroll_val)), True, (255, 255, 255)),
                        (100, 100))
            clock.tick(60)
            pygame.display.flip()

        pygame.display.quit()
