###################################################################################
# TO DO
# PRODUCTIVE
### TENTATIVE # FIX Resolve Pong lag/bugs
### TENTATIVE # GUI WCST revamp cards. Again.
### NO IMPACT BUG # FIX Pong display surface quit error (check if actual issue)
### TENTATIVE # FIX dynamic HR, threshold beats
### TENTATIVE # FIX dynamic HR, linear decrease
### RESOLVED # GUI increase size of text throughout
### RESOLVED ADD conditioning statement after POMS baseline ###################### ?
### RESOLVED # FIX driving game deviation calculation
### TENTATIVE # FIX driving game going over time limit
### RESOLVED # CHANGE driving and pong to 1 minute practice
### TENTATIVE # PROVIDE test data for ambient prime live session (Junk ID/Condition)
### RESOLVED # UPDATE ambient prime with proper labels (ID + condition string, not numbers)
### JURY RIG # FIX pong output metrics, only does travelling -> fix flags to output hits/misses

###################################################################################

from PyQt5.QtCore import *
import qdarkstyle
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import threading
from queue import Queue
from utils.Games import *
from utils.DataCollection import *
import pygame, sys, random
import webbrowser

real = True

header_font = QFont()
header_font.setPointSize(24)
header_font.setWeight(QFont.Bold)

body_font = QFont()
body_font.setPointSize(18)
body_font.setWeight(QFont.Normal)


class SelectionPage(QWidget):
    def __init__(self, parent=None):
        super(SelectionPage, self).__init__(parent)

        self.setGeometry(0, 0, 1920, 1080)

        self.cond1 = QPushButton('Condition STA: Static Soundscape', self)
        self.cond1.resize(400, 200)
        self.cond1.move(220, 20)
        self.cond1.setCheckable(True)
        self.cond1.setEnabled(True)


        self.cond2 = QPushButton('Condition STK: Stock Soundscape', self)
        self.cond2.resize(400, 200)
        self.cond2.move(self.width() - self.cond2.width() - 220 , 20)
        self.cond2.setCheckable(True)
        self.cond2.setEnabled(True)

        self.cond3 = QPushButton('Condition OA: Office Ambiance', self)
        self.cond3.resize(400, 200)
        self.cond3.move(220, 240)
        self.cond3.setCheckable(True)
        self.cond3.setEnabled(True)

        self.cond4 = QPushButton('Condition DYN: Dynamic Soundscape', self)
        self.cond4.resize(400, 200)
        self.cond4.move(self.width() - self.cond4.width() - 220, 240)
        self.cond4.setCheckable(True)
        self.cond4.setEnabled(True)

        self.prac = QPushButton('Attach Practice Session', self)
        self.prac.resize(400, 200)
        self.prac.move(220, 460)
        self.prac.setCheckable(False)
        self.prac.setEnabled(False)

        self.exper = QPushButton('No Practice Session', self)
        self.exper.resize(400, 200)
        self.exper.move(self.width() - self.exper.width() - 220, 460)
        self.exper.setCheckable(False)
        self.exper.setEnabled(False)

        self.add_final_poms = QPushButton('Attach Final POMS', self)
        self.add_final_poms.resize(400, 200)
        self.add_final_poms.move(220, 680)
        self.add_final_poms.setCheckable(False)
        self.add_final_poms.setEnabled(False)

        self.no_add_poms = QPushButton('No Final POMS', self)
        self.no_add_poms.resize(400, 200)
        self.no_add_poms.move(self.width() - self.exper.width() - 220, 680)
        self.no_add_poms.setCheckable(False)
        self.no_add_poms.setEnabled(False)

        self.startButton = QPushButton('Start!', self)
        self.startButton.resize(400, 200)
        self.startButton.move(self.width() / 2 - self.exper.width() / 2, self.height() - 220)
        self.startButton.setCheckable(False)
        self.startButton.setEnabled(False)


class StartPage(QWidget):
    def __init__(self, parent=None):
        super(StartPage, self).__init__(parent)

        self.setGeometry(0, 0, 1920, 1080)

        self.label = QLabel(self)
        self.pixmap = QPixmap('assets/title_screen.png').scaledToHeight(self.height() / 3)
        self.label.setPixmap(self.pixmap)
        self.label.move(self.width() / 2 - self.pixmap.width() / 2, 20)

        self.welcome_label = QLabel(self)
        self.welcome_label.setFont(header_font)
        self.welcome_label.setText("Welcome!")
        self.welcome_label.move(self.width() / 2 - self.welcome_label.width() /2, self.pixmap.height() + 100)

        self.instruction_label = QLabel(self)
        self.instruction_label.setFont(body_font)
        self.instruction_label.setText("Thanks for participating!\nClick the button below to proceed")
        self.instruction_label.setAlignment(Qt.AlignCenter)
        self.instruction_label.move(self.width() / 2 - 140, self.pixmap.height()+175)

        self.startButton = QPushButton('Start', self)
        self.startButton.setCheckable(True)
        self.startButton.resize(400, 100)
        self.startButton.move(self.width() / 2 - self.startButton.width() / 2, self.height() - 200)


class InitFixation(QWidget):
    def __init__(self, parent=None):
        super(InitFixation, self).__init__(parent)

        self.setGeometry(0, 0, 1920, 1080)

        self.label = QLabel(self)
        self.pixmap = QPixmap("assets/fixation_point.png")
        self.label.setPixmap(self.pixmap)
        self.label.move(self.width()/2 - self.pixmap.width()/2, self.height()/2 - self.pixmap.height()/2)

        self.text = QLabel(self)
        self.text.setText("During fixation periods, remember to focus on the target in the center\n"
                          "These sections maintain eye tracking calibration throughout the experiment and ensure accuracy")
        self.text.setFont(body_font)
        self.text.resize(1500,100)
        self.text.setAlignment(Qt.AlignCenter)
        self.text.move(self.width()/2 - self.text.width()/2, self.height()/3*2 - 50)

        self.nextButton = QPushButton('Tutorials', self)
        self.nextButton.setEnabled(False)
        self.nextButton.setCheckable(False)
        self.nextButton.resize(400, 100)
        self.nextButton.move(self.width()/2 - self.nextButton.width()/2, self.height()/4*3)


class StandardFixation(QWidget):
    def __init__(self, parent=None):
        super(StandardFixation, self).__init__(parent)

        self.setGeometry(0, 0, 1920, 1080)

        self.label = QLabel(self)
        self.pixmap = QPixmap("assets/fixation_point.png")
        self.label.setPixmap(self.pixmap)
        self.label.move(self.width()/2 - self.pixmap.width()/2, self.height()/2 - self.pixmap.height()/2)


class EndPractice(QWidget):
    def __init__(self, parent=None):
        super(EndPractice, self).__init__(parent)

        self.setGeometry(0, 0, 1920, 1080)
        header_font.setUnderline(False)
        self.text = QLabel(self)
        self.text.setText("This concludes the Practice round! During the experiment, you will \n"
                          "complete the same tasks and questionnaires.\n\n"
                          "Please contact your administrator by raising your hand to continue the experiment\n\n\n"
                          "When your administrator gives the okay, click the button below to proceed!")
        self.text.setFont(header_font)
        self.text.resize(1500, 500)
        self.text.setAlignment(Qt.AlignCenter)
        self.text.move(self.width() / 2 - self.text.width() / 2, self.height() / 3 - self.text.height()/2)

        self.startbtn = QPushButton('Next!', self)
        self.startbtn.setEnabled(True)
        self.startbtn.setCheckable(True)
        self.startbtn.resize(400, 100)
        self.startbtn.move(self.width() / 2 - self.startbtn.width() / 2, self.height() / 4 * 3)


class ConditioningScreen(QWidget):
    def __init__(self, parent=None):
        super(ConditioningScreen, self).__init__(parent)

        self.setGeometry(0, 0, 1920, 1080)

        self.text = QLabel(self)
        self.text.setText("Please raise your hand and wait until the experimenter speaks to you")
        self.text.setFont(header_font)
        self.text.resize(1500, 500)
        self.text.setAlignment(Qt.AlignCenter)
        self.text.move(self.width() / 2 - self.text.width() / 2, self.height() / 3 - self.text.height()/2)

        self.startbtn = QPushButton('Start Experiment!', self)
        self.startbtn.setEnabled(True)
        self.startbtn.setCheckable(True)
        self.startbtn.resize(400, 100)
        self.startbtn.move(self.width() / 2 - self.startbtn.width() / 2, self.height() / 4 * 3)


# class CreativityTransition(QWidget):
#     def __init__(self, parent=None):
#         super(CreativityTransition, self).__init__(parent)
#
#         self.setGeometry(0, 0, 1920, 1080)
#
#         self.text = QLabel(self)
#         self.text.setText("This concludes the Practice round! During the experiment, you will \n"
#                           "complete the same tasks and questionnaires.\n\n"
#                           "Please speak to the experimenter now.")
#         self.text.setFont(header_font)
#         self.text.resize(1000, 500)
#         self.text.setAlignment(Qt.AlignCenter)
#         self.text.move(self.width() / 2 - self.text.width() / 2, self.height() / 3 )
#
#         self.startbtn = QPushButton('Start Experiment!', self)
#         self.startbtn.setEnabled(True)
#         self.startbtn.setCheckable(True)
#         self.startbtn.resize(400, 100)
#         self.startbtn.move(self.width() / 2 - self.startbtn.width() / 2, self.height() / 4 * 3)
#

class End(QWidget):
    def __init__(self, parent=None):
        super(End, self).__init__(parent)

        self.setGeometry(0, 0, 1920, 1080)

        self.text = QLabel(self)
        self.text.setText("This session ends here and your 5 minute break begins.\nPlease raise your hand and wait until the experimenter speaks to you")
        self.text.setFont(header_font)
        self.text.resize(1500, 500)
        self.text.setAlignment(Qt.AlignCenter)
        self.text.move(self.width() / 2 - self.text.width() / 2, self.height() / 3 - self.text.height() / 2)

###################################################################################


class WCSTTutorial(QWidget):
    def __init__(self, task_q, bio_q_algo, condition, parent=None):
        super(WCSTTutorial, self).__init__(parent)

        self.task_q = task_q

        self.bio_q_algo = bio_q_algo
        self.condition = condition

        self.wcst1 = None
        self.wcst2 = None
        self.wcst3 = None

        self.setGeometry(0, 0, 1920, 1080)

        # Need text description of WCST

        self.label1 = QLabel(self)
        self.pixmap = QPixmap('assets/WCST/goal.png').scaledToHeight(450)
        self.label1.setPixmap(self.pixmap)
        self.label1.move(self.width() - self.pixmap.width()-20, 75)

        self.label2 = QLabel(self)
        self.label2.setText("Each circle below represents a possible correct sort.\n"
                            "From left to right, the lower card could be sorted by color, number, or shape")
        # CARD BELOW, CLICK CARD ABOVE THAT MATCHES CARD BELOW.
        # YOU ARE NOT TOLD THE SORT RULE, NOT TOLD WHEN RULE CHANGES OR WHAT IT CHANGES TO
        # DISCOVER NEW RULE EACH TIME IT CHANGES
        self.label2.setFont(body_font)
        self.label2.move(self.width() - self.pixmap.width(), 20)

        self.label3 = QLabel(self)
        self.pixmap = QPixmap('assets/WCST/start.png').scaledToHeight(450)
        self.label3.setPixmap(self.pixmap)
        self.label3.move(20, 75)

        self.title = QLabel(self)
        self.title.setText("Card Sorting Task")
        header_font.setUnderline(True)
        self.title.setFont(header_font)
        self.title.move(20, 540)

        self.descriptionA = QLabel(self)
        self.descriptionA.setText("In this task, you will sort the lower card by clicking on one of the four upper\n"
                                  "cards.\n\n There are three possible ways to sort the lower card, by color, by shape,\n"
                                  "or by number of shapes\n\n"
                                  "The sort rule is not shown and you will have to guess it by picking one of the four\n"
                                  "upper cards and narrowing it down\n\n"
                                  "Click each of the tutorial buttons (to the right) to provide an introduction to each sort rule\n\n"
                                  "You must complete all 3 tutorials before the next tutorial will become available\n\n")
        # CARD BELOW, CLICK CARD ABOVE THAT MATCHES CARD BELOW.
        # YOU ARE NOT TOLD THE SORT RULE, NOT TOLD WHEN RULE CHANGES OR WHAT IT CHANGES TO
        # DISCOVER NEW RULE EACH TIME IT CHANGES
        self.descriptionA.setFont(body_font)
        self.descriptionA.move(20, 580)


        self.startbtn = QPushButton("Next Tutorial", self)
        if real == True:
            self.startbtn.setCheckable(False)
            self.startbtn.setEnabled(False)
        self.startbtn.resize(300, 520)
        self.startbtn.move(self.width() - 300 - 20, self.height() - 20 - 520)

        self.sample1btn = QPushButton("Practice: Sort by Number", self)
        self.sample1btn.setCheckable(True)
        self.sample1btn.setEnabled(True)
        self.sample1btn.resize(300, 160)
        self.sample1btn.move(self.width() - 600 - 40, self.height() - 160 * 3 - 20 * 3)

        self.sample2btn = QPushButton("Practice: Sort by Color", self)
        self.sample2btn.setCheckable(False)
        self.sample2btn.setEnabled(False)
        self.sample2btn.resize(300, 160)
        self.sample2btn.move(self.width() - 600 - 40, self.height() - 160 * 2 - 20 * 2)

        self.sample3btn = QPushButton("Practice: Sort by Shape", self)
        self.sample3btn.setCheckable(False)
        self.sample3btn.setEnabled(False)
        self.sample3btn.resize(300, 160)
        self.sample3btn.move(self.width() - 600 - 40, self.height() - 160 - 20)

    def sampleWCST1(self):
        self.wcst1 = WisconsinCardSort(self.task_q, self.bio_q_algo, self.condition, 5, 'number', 'trial')

        self.sample1btn.setCheckable(False)
        self.sample1btn.setEnabled(False)
        self.sample2btn.setCheckable(True)
        self.sample2btn.setEnabled(True)
        self.sample2btn.setChecked(True)

        return

    def sampleWCST2(self):
        self.wcst2 = WisconsinCardSort(self.task_q,self.bio_q_algo, self.condition, 5, 'color', 'trial')

        self.sample2btn.setCheckable(False)
        self.sample2btn.setEnabled(False)
        self.sample3btn.setCheckable(True)
        self.sample3btn.setEnabled(True)
        self.sample3btn.setChecked(True)


        return


    def sampleWCST3(self):
        self.wcst3 = WisconsinCardSort(self.task_q, self.bio_q_algo, self.condition, 5, 'shape', 'trial')

        self.sample3btn.setCheckable(False)
        self.sample3btn.setEnabled(False)
        self.startbtn.setCheckable(True)
        self.startbtn.setEnabled(True)
        self.startbtn.setChecked(True)

        return


class PongTutorial(QWidget):
    def __init__(self, task_q, bio_q_algo, condition, parent=None):
        super(PongTutorial, self).__init__(parent)

        self.task_q = task_q

        self.bio_q_algo = bio_q_algo
        self.condition = condition

        self.pong1 = None
        self.pong2 = None
        self.pong3 = None

        self.setGeometry(0, 0, 1920, 1080)

        self.startbtn = QPushButton("Next Tutorial", self)
        if real == True:
            self.startbtn.setCheckable(False)
            self.startbtn.setEnabled(False)
        self.startbtn.resize(300, 520)
        self.startbtn.move(self.width() - 300 - 20, self.height() - 20 - 520)


        self.label1 = QLabel(self)
        self.pixmap = QPixmap('assets/pong/pong_ex.png').scaledToHeight(500)
        self.label1.setPixmap(self.pixmap)
        self.label1.move(20, 20)

        self.sample2btn = QPushButton("1 Minute Trial", self)
        self.sample2btn.setCheckable(True)
        self.sample2btn.setEnabled(True)
        self.sample2btn.resize(300, 520)
        self.sample2btn.move(self.width() - 640, self.height() - 520 - 20 )

        self.title = QLabel(self)
        self.title.setText("Pong Task")
        header_font.setUnderline(True)
        self.title.setFont(header_font)
        self.title.move(20, 540)

        self.descriptionA = QLabel(self)
        self.descriptionA.setText("In this task, you will be playing classic Pong\n\n"
                                  "Use the mouse/trackpad to control the position of paddle\n\n"
                                  "Score 1 point every time you serve the ball to your opponent\n\n"
                                  "If your opponent misses, you score 5 points\n\n"
                                  "If you miss the ball, the score is reset to zero. Score as many points as possible\n\n"
                                  "As you score more points, the ball moves faster")

        self.descriptionA.setFont(body_font)
        self.descriptionA.move(20, 580)

    def samplePong1(self):
        self.pong = PongGame(self.task_q, self.bio_q_algo, self.condition, 'trial')

        self.sample2btn.setCheckable(False)
        self.sample2btn.setEnabled(False)
        self.startbtn.setCheckable(True)
        self.startbtn.setEnabled(True)

        return


class DrivingTutorial(QWidget):
    def __init__(self, task_q, bio_q_algo, condition, parent=None):
        super(DrivingTutorial, self).__init__(parent)

        self.setGeometry (0, 0, 1920, 1080)
        self.task_q = task_q

        self.bio_q_algo = bio_q_algo
        self.condition = condition

        self.startbtn = QPushButton("Next Tutorial", self)
        if real == True:
            self.startbtn.setCheckable(False)
            self.startbtn.setEnabled(False)
        self.startbtn.resize(300, 520)
        self.startbtn.move(self.width() - 300 - 20, self.height() - 20 - 520)

        self.label = QLabel(self)
        self.pixmap = QPixmap('assets/racing/driving_ex.png').scaledToHeight(500)
        self.label.setPixmap(self.pixmap)
        self.label.move(20, 20)

        # self.label2 = QLabel(self)
        # self.pixmap = QPixmap('assets/racing/arrow-keys.png').scaledToHeight(500)
        # self.label2.setPixmap(self.pixmap)
        # self.label2.move(self.width() - self.pixmap.width()-20, 20)

        self.sample2btn = QPushButton("1 Minute Trial", self)
        self.sample2btn.setCheckable(True)
        self.sample2btn.setEnabled(True)
        self.sample2btn.resize(300, 520)
        self.sample2btn.move(self.width() - 640, self.height() - 520 - 20)

        self.title = QLabel(self)
        self.title.setText("Driving Task")
        header_font.setUnderline(True)
        self.title.setFont(header_font)
        self.title.move(20, 540)

        self.descriptionA = QLabel(self)
        self.descriptionA.setText("In this task, you will be playing a top-down driving game\n\n"
                                  "You can use the left and right arrow keys to navigate the road\n\n"
                                  "Your goal is to drive as far as possible within the time frame\n\n"
                                  "Your car's speed is dependant on how far you steer from the center of the lane\n\n"
                                  "The closer to the center you are, the faster you will drive.\n\n"
                                  "If you drive off the road, your speed will drop drastically, reducing the total\n"
                                  "distance you can drive\n\n")

        self.descriptionA.setFont(body_font)
        self.descriptionA.move(20, 580)


    def sampleDriving1(self):
        self.driving = DrivingGame(self.task_q, self.bio_q_algo, self.condition, 'trial')

        self.sample2btn.setCheckable(False)
        self.sample2btn.setEnabled(False)
        self.startbtn.setCheckable(True)
        self.startbtn.setEnabled(True)

        return


###################################################################################

class Session(QWidget):
    def __init__(self, parent=None):
        super(Session, self).__init__(parent)

        self.setGeometry(0, 0, 1920, 1080)

        self.next_task = QPushButton("Next Task", self)
        self.next_task.setCheckable(True)
        self.next_task.setEnabled(True)
        self.next_task.resize(300, 280)
        self.next_task.move(self.width() / 2 - 150, self.height() / 2 - 140)


# class CreativeActivityOne(QWidget):
#     def __init__(self, parent=None):
#         super(CreativeActivityOne, self).__init__(parent)
#
#         self.setGeometry(0, 0, 1920, 1080)
#
#         self.text = QLabel(self)
#         self.text.setText("Zobrist Cube")
#         self.text.setFont(header_font)
#         self.text.resize(1000, 500)
#         self.text.setAlignment(Qt.AlignCenter)
#         self.text.move(self.width() / 2 - self.text.width() / 2, self.height() / 3 )
#
#         self.startbtn = QPushButton('Start Experiment!', self)
#         self.startbtn.setEnabled(True)
#         self.startbtn.setCheckable(True)
#         self.startbtn.resize(400, 100)
#         self.startbtn.move(self.width() / 2 - self.startbtn.width() / 2, self.height() / 4 * 3)
#
#
# class CreativeActivityTwo(QWidget):
#     def __init__(self, parent=None):
#         super(CreativeActivityTwo, self).__init__(parent)
#
#         self.setGeometry(0, 0, 1920, 1080)
#
#         self.text = QLabel(self)
#         self.text.setText("Bananagrams")
#         self.text.setFont(header_font)
#         self.text.resize(1000, 500)
#         self.text.setAlignment(Qt.AlignCenter)
#         self.text.move(self.width() / 2 - self.text.width() / 2, self.height() / 3 )
#
#         self.startbtn = QPushButton('Start Experiment!', self)
#         self.startbtn.setEnabled(True)
#         self.startbtn.setCheckable(True)
#         self.startbtn.resize(400, 100)
#         self.startbtn.move(self.width() / 2 - self.startbtn.width() / 2, self.height() / 4 * 3)
#


###################################################################################


class PomsQuestionnaire(QWidget):
    def __init__(self, task_q, question, status, parent=None):
        super(PomsQuestionnaire, self).__init__(parent)

        self.setGeometry(0, 0, 1920, 1080)

        self.q = task_q

        radio_font = QFont()
        radio_font.setPointSize(34)
        radio_font.setBold(True)

        q_font = QFont()
        q_font.setPointSize(20)

        emotion_font = QFont()
        emotion_font.setPointSize(48)
        emotion_font.setWeight(QFont.ExtraBold)

        self.title = QLabel("Mood Questionnaire", self)
        self.title.setFont(header_font)
        self.title.setAlignment(Qt.AlignCenter)
        self.title.resize(400,100)
        self.title.move(self.width()/2 - self.title.width()/2 - 300, 20)

        if question == 'intro':
            self.label = QLabel ("The following questions are feelings that people have.\n"
                                 "Please select the value for each that BEST describes you now.", self)
            self.startbtn = QPushButton("Next", self)
            self.startbtn.resize(400, 100)
            self.startbtn.move(self.width() / 2 - self.startbtn.width() / 2 - 300, self.height() * 3 / 4)

        elif question == 'outro':
            self.label = QLabel ("Press to continue the experiment", self)
            self.startbtn = QPushButton("Next", self)
            self.startbtn.resize(400, 100)
            self.startbtn.move(self.width() / 2 - self.startbtn.width() / 2 - 300, self.height() * 3 / 4)
        else:
            self.label = QLabel ("Which choice best describes how you feel RIGHT NOW\nin regards to the following: ", self)


            self.emotion = QLabel (question[0], self)
            self.emotion.setFont(emotion_font)
            self.emotion.setAlignment(Qt.AlignCenter)
            self.emotion.resize(800,100)
            self.emotion.move(self.width()/2 - self.emotion.width()/2 - 300, 600)

            header_font.setUnderline(False)

            self.choice1 = QRadioButton("Not at all", self)
            self.choice1.setFont(header_font)
            self.choice1.resize(200,200)
            self.choice1.move(self.width() - self.choice1.width() - 220, 50)

            self.choice2 = QRadioButton("A little", self)
            self.choice2.setFont(header_font)
            self.choice2.resize(200,200)
            self.choice2.move(self.width() - self.choice2.width() - 220, 250)

            self.choice3 = QRadioButton("Moderately", self)
            self.choice3.setFont(header_font)
            self.choice3.resize(200,200)
            self.choice3.move(self.width() - self.choice3.width() - 220, 450)

            self.choice4 = QRadioButton("Quite a lot", self)
            self.choice4.setFont(header_font)
            self.choice4.resize(200,200)
            self.choice4.move(self.width() - self.choice4.width() - 220, 650)

            self.choice5 = QRadioButton("Extremely", self)
            self.choice5.setFont(header_font)
            self.choice5.resize(200,200)
            self.choice5.move(self.width() - self.choice5.width() - 220,  850)

        header_font.setUnderline(False)
        self.label.setFont(header_font)
        self.label.resize(1500, 200)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.move(self.width() / 2 - self.label.width()/2 - 300, 200)


class AmbientPrimePractice(QWidget):
    def __init__(self, task_q, id, condition, parent=None):
        super(AmbientPrimePractice, self).__init__(parent)

        self.setGeometry(0, 0, 1920, 1080)

        self.q = task_q
        self.condition = condition
        self.id = id

        self.label = QLabel("Through the experiment, you will occasionally be redirected to a web survey\n"
                            "Simply follow the on screen directions of the survey, after you will be redirected back", self)
        self.label.setFont(body_font)
        self.label.resize(1000, 200)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.move(self.width() / 2 - self.label.width() / 2, 100)

        self.startbtn = QPushButton("Next", self)
        self.startbtn.resize(400, 100)
        self.startbtn.setCheckable(False)
        self.startbtn.setEnabled(False)
        self.startbtn.move(self.width() / 2 - self.startbtn.width() / 2, self.height() - 20 - 300)

        self.startambient = QPushButton("Start Ambient Prime Survey!", self)
        self.startambient.resize(400, 100)
        self.startambient.setCheckable(True)
        self.startambient.setEnabled(True)
        self.startambient.move(self.width() / 2 - self.startbtn.width() / 2, self.height() - 20 - 320 - 100)

        if real:
            print("proceed as normal")
        else:
            self.enableButton()

    def enableButton(self):
        self.startbtn.setCheckable(True)
        self.startbtn.setEnabled(True)

    def ambientPrimeStart(self):
        cond_string = ""
        if self.condition == 1:
            cond_string = "STA"
        elif self.condition == 2:
            cond_string = "STK"
        elif self.condition == 3:
            cond_string = "OA"
        elif self.condition == 4:
            cond_string = "DYN"

        self.enableButton()
        link = "http://prime.sentientdecisionscience.com/?RespId=" + str(self.id) + cond_string + "&ProjectId=061510f2d76a7658619aed29c4da3ae0&Ex=1,2"
        webbrowser.open(link)


class AmbientPrimePost(QWidget):
    def __init__(self, task_q, id, condition, parent=None):
        super(AmbientPrimePost, self).__init__(parent)

        self.setGeometry(0, 0, 1920, 1080)

        self.q = task_q
        self.id = id
        self.condition = condition

        self.startbtn = QPushButton("Next", self)
        self.startbtn.resize(400, 100)
        self.startbtn.move(self.width()/2 - self.startbtn.width()/2, self.height() - 20 - 280)

        cond_string = ""
        if self.condition == 1:
            cond_string = "STA"
        elif self.condition == 2:
            cond_string = "STK"
        elif self.condition == 3:
            cond_string = "OA"
        elif self.condition == 4:
            cond_string = "DYN"

        link =  "http://prime.sentientdecisionscience.com/?RespId=" + str(self.id) + cond_string + "&ProjectId=4d467347f2365f95cb32ca25ad0c8f05&Ex=1,2"

        webbrowser.open(link)

        if real:
            QTimer.singleShot(3000, self.enableButton)
        else:
            self.enableButton()

    def enableButton(self):
        self.startbtn.setCheckable(True)
        self.startbtn.setEnabled(True)


# class CreativityEvaluation(QWidget):
#     def __init__(self, task_q, id, parent=None):
#         super(CreativityEvaluation, self).__init__(parent)
#
#         self.setGeometry(0, 0, 1920, 1080)
#
#         self.q = task_q
#
#         self.title = QLabel("Creativity Evaluation", self)
#         self.title.setFont(header_font)
#         self.title.setAlignment(Qt.AlignCenter)
#         self.title.resize(400, 50)
#         self.title.move(self.width() / 2 - self.title.width() / 2, 20)
#
#         self.startbtn = QPushButton("Next", self)
#         self.startbtn.resize(400, 100)
#         self.startbtn.move(self.width() / 2 - self.startbtn.width() / 2, self.height() - 20 - 100)
#
#         self.slider1label = QLabel("Overall, how creative are you?", self)
#         self.slider1label.setFont(header_font)
#         self.slider1label.setAlignment(Qt.AlignCenter)
#         self.slider1label.resize(1000, 75)
#         self.slider1label.move(self.width() / 2 - self.slider1label.width() / 2, self.height()/4-150)
#
#         self.slider1 = QSlider(Qt.Horizontal, self)
#         self.slider1.setFocusPolicy(Qt.StrongFocus)
#         self.slider1.setTickPosition(QSlider.TicksBothSides)
#         self.slider1.setTickInterval(10)
#         self.slider1.setSingleStep(1)
#         self.slider1.resize(500,100)
#         self.slider1.move(self.width() / 2 - self.slider1.width()/2, self.height()/4 - 100)
#
#         self.slider2label = QLabel("When it comes to your use of language (e.g. speaking or writing),\n"
#                                    "how creative do you consider yourself?", self)
#         self.slider2label.setFont(header_font)
#         self.slider2label.setAlignment(Qt.AlignCenter)
#         self.slider2label.resize(1000, 75)
#         self.slider2label.move(self.width() / 2 - self.slider1label.width() / 2, self.height() * 2 / 4 - 200)
#
#         self.slider2 = QSlider(Qt.Horizontal, self)
#         self.slider2.setFocusPolicy(Qt.StrongFocus)
#         self.slider2.setTickPosition(QSlider.TicksBothSides)
#         self.slider2.setTickInterval(10)
#         self.slider2.setSingleStep(1)
#         self.slider2.resize(500, 100)
#         self.slider2.move(self.width() / 2 - self.slider1.width() / 2, self.height() * 2 / 4 - 100)
#
#         self.slider3label = QLabel("When it comes to visually oriented activities (e.g. drawing or manipulating objects),\n"
#                                    "how creative do you consider yourself?", self)
#         self.slider3label.setFont(header_font)
#         self.slider3label.setAlignment(Qt.AlignCenter)
#         self.slider3label.resize(1000, 75)
#         self.slider3label.move(self.width() / 2 - self.slider1label.width() / 2, self.height() * 3 / 4 - 200)
#
#         self.slider3 = QSlider(Qt.Horizontal, self)
#         self.slider3.setFocusPolicy(Qt.StrongFocus)
#         self.slider3.setTickPosition(QSlider.TicksBothSides)
#         self.slider3.setTickInterval(10)
#         self.slider3.setSingleStep(1)
#         self.slider3.resize(500, 100)
#         self.slider3.move(self.width() / 2 - self.slider1.width() / 2, self.height() * 3 / 4 - 100)

###################################################################################


class FaderWidget(QWidget):

    def __init__(self, old_widget, new_widget):
        QWidget.__init__(self, new_widget)

        self.old_pixmap = QPixmap(new_widget.size())
        old_widget.render(self.old_pixmap)
        self.pixmap_opacity = 1.0

        self.timeline = QTimeLine()
        self.timeline.valueChanged.connect(self.animate)
        self.timeline.finished.connect(self.close)
        self.timeline.setDuration(333)
        self.timeline.start()

        self.resize(new_widget.size())
        self.show()

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        painter.setOpacity(self.pixmap_opacity)
        painter.drawPixmap(0, 0, self.old_pixmap)
        painter.end()

    def animate(self, value):
        self.pixmap_opacity = 1.0 - value
        self.repaint()


class ProductiveStackFlow(QStackedWidget):
    def __init__(self, condition, participant_id, parent=None):
        QStackedWidget.__init__(self, parent)
        self.setGeometry(0, 0, 1920, 1080)

        self.participant_id = participant_id
        self.condition = condition
        self.cur_index = 0
        self.task_q = Queue()
        self.bio_q = Queue()
        self.bio_q_algo = Queue()

        self.practice = True
        self.final_poms = False

        self.task_q.put({'task_name': 'start', 'metrics': {1: 'start', 2: -1, 3: -1, 4: -1, 5: -1, 6: -1, 7: -1}})

        pygame.init()
        pygame.mixer.init()

        self.ambiance = pygame.mixer.Sound("soundscapes/Brody_Office_Ambience_Loop_1.ogg")
        self.ambiance.set_volume(0.05)
        
        if condition == 1:
            self.intro = pygame.mixer.Sound("soundscapes/1_BRODY_SONIC_JOURNEY_v2_ENTRAINMENT.ogg")
            self.body = pygame.mixer.Sound("soundscapes/1_BRODY_SONIC_JOURNEY_v2_MAIN_MUSIC_SD_BIN_PULSE80.ogg")
            self.outro = pygame.mixer.Sound("soundscapes/1_BRODY_SONIC_JOURNEY_v2_RETURN.ogg")
        elif condition == 2:
            self.intro = pygame.mixer.Sound("soundscapes/2_BRODY_STOCK_INTRO.ogg")
            self.body = pygame.mixer.Sound("soundscapes/2_BRODY_STOCK EQUIVALENT.ogg")
            self.outro = pygame.mixer.Sound("soundscapes/2_BRODY_STOCK_RETURN.ogg")
        elif condition == 3:
            print ("OFFICE AMBIANCE")
            self.intro = None
            self.body = self.ambiance
            self.outro = None
        elif condition == 4:
            self.intro = pygame.mixer.Sound("soundscapes/4_BRODY_SONIC_JOURNEY_v2_ENTRAINMENT_DYNAMIC.ogg")
            self.body = pygame.mixer.Sound("soundscapes/4_BRODY_SONIC_JOURNEY_v2_MAIN_DYNAMIC.ogg")
            self.outro = pygame.mixer.Sound("soundscapes/4_BRODY_SONIC_JOURNEY_v2_RETURN DYNAMIC.ogg")
            self.beat = pygame.mixer.Sound("soundscapes/4_BRODY_SONIC_JOURNEY_v2_SINGLE_BEAT_DYNAMIC.ogg")

    def setCurrentIndex(self, index):
        self.fader_widget = FaderWidget(self.currentWidget(), self.widget(index))
        QStackedWidget.setCurrentIndex(self, index)

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            sys.exit()

    def startBiometrics(self):
        self.eye_tracker = BiometricTracking(self.bio_q, self.bio_q_algo)

    def startDataLogger(self):
        self.data_logger = DataLogger(self.bio_q, self.task_q, self.participant_id, self.condition)

    def cleanStack(self):
        print("cleaning!")
        widget = self.widget(0)
        self.removeWidget(widget)
        widget.setParent(None)

    def setSelectionPage(self):
        def cond1():
            self.condition = 1
            self.currentWidget().exper.setCheckable(True)
            self.currentWidget().prac.setCheckable(True)
            self.currentWidget().exper.setEnabled(True)
            self.currentWidget().prac.setEnabled(True)


        def cond2():
            self.condition = 2
            self.currentWidget().exper.setCheckable(True)
            self.currentWidget().prac.setCheckable(True)
            self.currentWidget().exper.setEnabled(True)
            self.currentWidget().prac.setEnabled(True)

        def cond3():
            self.condition = 3
            self.currentWidget().exper.setCheckable(True)
            self.currentWidget().prac.setCheckable(True)
            self.currentWidget().exper.setEnabled(True)
            self.currentWidget().prac.setEnabled(True)

        def cond4():
            self.condition = 4
            self.currentWidget().exper.setCheckable(True)
            self.currentWidget().prac.setCheckable(True)
            self.currentWidget().exper.setEnabled(True)
            self.currentWidget().prac.setEnabled(True)

        def exper():
            self.practice = False
            self.currentWidget().add_final_poms.setCheckable(True)
            self.currentWidget().no_add_poms.setCheckable(True)
            self.currentWidget().add_final_poms.setEnabled(True)
            self.currentWidget().no_add_poms.setEnabled(True)

        def prac():
            self.practice = True
            self.currentWidget().add_final_poms.setCheckable(True)
            self.currentWidget().no_add_poms.setCheckable(True)
            self.currentWidget().add_final_poms.setEnabled(True)
            self.currentWidget().no_add_poms.setEnabled(True)

        def add_final_poms():
            self.final_poms = True
            self.currentWidget().startButton.setCheckable(True)
            self.currentWidget().startButton.setEnabled(True)

        def no_add_final():
            self.final_poms = False
            self.currentWidget().startButton.setCheckable(True)
            self.currentWidget().startButton.setEnabled(True)

        def update():
            self.beat = None

            if self.condition == 1:
                self.intro = pygame.mixer.Sound("soundscapes/1_BRODY_SONIC_JOURNEY_v2_ENTRAINMENT.ogg")
                self.body = pygame.mixer.Sound("soundscapes/1_BRODY_SONIC_JOURNEY_v2_MAIN_MUSIC_SD_BIN_PULSE80.ogg")
                self.outro = pygame.mixer.Sound("soundscapes/1_BRODY_SONIC_JOURNEY_v2_RETURN.ogg")
            elif self.condition == 2:
                self.intro = pygame.mixer.Sound("soundscapes/2_BRODY_STOCK_INTRO.ogg")
                self.body = pygame.mixer.Sound("soundscapes/2_BRODY_STOCK EQUIVALENT.ogg")
                self.outro = pygame.mixer.Sound("soundscapes/2_BRODY_STOCK_RETURN.ogg")
            elif self.condition == 3:
                print("OFFICE AMBIANCE")
                self.intro = None
                self.body = self.ambiance
                self.outro = None
            elif self.condition == 4:
                self.intro = pygame.mixer.Sound("soundscapes/4_BRODY_SONIC_JOURNEY_v2_ENTRAINMENT_DYNAMIC.ogg")
                self.body = pygame.mixer.Sound("soundscapes/4_BRODY_SONIC_JOURNEY_v2_MAIN_DYNAMIC.ogg")
                self.outro = pygame.mixer.Sound("soundscapes/4_BRODY_SONIC_JOURNEY_v2_RETURN DYNAMIC.ogg")
                self.beat = pygame.mixer.Sound("soundscapes/4_BRODY_SONIC_JOURNEY_v2_SINGLE_BEAT_DYNAMIC.ogg")
            if self.intro is not None:
                self.intro.set_volume(0.075)
            self.body.set_volume(0.075)
            if self.outro is not None:
                self.outro.set_volume(0.075)
            if self.beat is not None:
                self.beat.set_volume(0.075)

            threading.Thread(name="Biometrics Tracker", target=self.startBiometrics).start()
            threading.Thread(name="Data Logger", target=self.startDataLogger).start()

            self.setStartPage()

        self.task_q.put({'task_name': 'selection_page', 'metrics': {1: -1, 2: -1, 3: -1, 4: -1, 5: -1, 6: -1, 7: -1}})

        self.addWidget(SelectionPage())

        self.setCurrentWidget(self.widget(0))

        self.currentWidget().cond1.clicked.connect(cond1)
        self.currentWidget().cond2.clicked.connect(cond2)
        self.currentWidget().cond3.clicked.connect(cond3)
        self.currentWidget().cond4.clicked.connect(cond4)

        self.currentWidget().prac.clicked.connect(prac)
        self.currentWidget().exper.clicked.connect(exper)

        self.currentWidget().add_final_poms.clicked.connect(add_final_poms)
        self.currentWidget().no_add_poms.clicked.connect(no_add_final)


        self.currentWidget().startButton.clicked.connect(update)

    def setStartPage(self):
        self.task_q.put({'task_name': 'start_page', 'metrics': {1: -1, 2: -1, 3: -1, 4: -1, 5: -1, 6: -1, 7: -1}})

        self.addWidget(StartPage())

        self.setCurrentIndex(1)
        self.setCurrentWidget(self.widget(1))

        self.cleanStack()
        if self.practice:
            self.currentWidget().startButton.clicked.connect(self.setInitFixation)
        else:
            self.currentWidget().startButton.clicked.connect(self.setAmbienceFixation)

    def setInitFixation(self):
        def enableButton():
            self.currentWidget().nextButton.setChecked(False)
            self.currentWidget().nextButton.setEnabled(True)
            self.currentWidget().nextButton.setCheckable(True)

        self.task_q.put({'task_name': 'init_fixation', 'metrics': {1: -1, 2: -1, 3: -1, 4: -1, 5: -1, 6: -1, 7: -1}})

        self.addWidget(InitFixation())

        self.setCurrentIndex(1)
        self.setCurrentWidget(self.widget(1))

        self.cleanStack()
        if real:
            QTimer.singleShot(10000, enableButton)
        else:
            QTimer.singleShot(1, enableButton)


        self.currentWidget().nextButton.clicked.connect(self.setWCSTTutorial)

    def setWCSTTutorial(self):
        self.addWidget(WCSTTutorial(self.task_q, self.bio_q_algo, self.condition))

        self.task_q.put({'task_name': 'wcst_tutorial', 'metrics': {1: -1, 2: -1, 3: -1, 4: -1, 5: -1, 6: -1, 7: -1}})

        self.setCurrentIndex(1)
        self.setCurrentWidget(self.widget(1))

        self.cleanStack()

        self.currentWidget().sample1btn.clicked.connect(self.currentWidget().sampleWCST1)
        self.currentWidget().sample2btn.clicked.connect(self.currentWidget().sampleWCST2)
        self.currentWidget().sample3btn.clicked.connect(self.currentWidget().sampleWCST3)

        self.currentWidget().startbtn.clicked.connect(self.setPongTutorial)

    def setPongTutorial(self):
        self.addWidget(PongTutorial(self.task_q, self.bio_q_algo, self.condition))

        self.task_q.put({'task_name': 'pong_tutorial', 'metrics': {1: -1, 2: -1, 3: -1, 4: -1, 5: -1, 6: -1, 7: -1}})

        self.setCurrentIndex(1)
        self.setCurrentWidget(self.widget(1))

        self.cleanStack()

        self.currentWidget().sample2btn.clicked.connect(self.currentWidget().samplePong1)

        self.currentWidget().startbtn.clicked.connect(self.setDrivingTutorial)

    def setDrivingTutorial(self):
        self.addWidget(DrivingTutorial(self.task_q, self.bio_q_algo, self.condition))

        self.task_q.put({'task_name': 'driving_tutorial', 'metrics': {1: -1, 2: -1, 3: -1, 4: -1, 5: -1, 6: -1, 7: -1}})

        self.setCurrentIndex(1)
        self.setCurrentWidget(self.widget(1))

        self.cleanStack()

        self.currentWidget().sample2btn.clicked.connect(self.currentWidget().sampleDriving1)

        self.currentWidget().startbtn.clicked.connect(self.setAmbientPrimePractice)

    def setAmbientPrimePractice(self):
        self.addWidget(AmbientPrimePractice(self.task_q, self.participant_id, self.condition))

        self.task_q.put(
            {'task_name': 'ambient_prime_pre', 'metrics': {1: -1, 2: -1, 3: -1, 4: -1, 5: -1, 6: -1, 7: -1}})

        self.setCurrentIndex(1)
        self.setCurrentWidget(self.widget(1))

        self.cleanStack()

        self.currentWidget().startbtn.clicked.connect(self.setPracticeTransition)
        self.currentWidget().startambient.clicked.connect(self.currentWidget().ambientPrimeStart)

    def setPracticeTransition(self):
        self.addWidget(EndPractice())

        self.task_q.put({'task_name': 'end_practice', 'metrics': {1: -1, 2: -1, 3: -1, 4: -1, 5: -1, 6: -1, 7: -1}})

        self.setCurrentIndex(1)
        self.setCurrentWidget(self.widget(1))

        self.cleanStack()

        self.currentWidget().startbtn.clicked.connect(self.setPOMSBaseline)

    def setPOMSBaseline(self):
        def init_questionnare():
            q = {}

            q[0] = ['tense', 'TEN', -1]
            if real:
                q[1] = ['angry', 'ANG', -1]
                q[2] = ['worn out', 'FAT', -1]
                q[3] = ['unhappy', 'DEP', -1]
                q[4] = ['proud', 'ERA', -1]
                q[5] = ['lively', 'VIG', -1]
                q[6] = ['confused', 'CON', -1]
                q[7] = ['sad', 'DEP', -1]
                q[8] = ['active', 'VIG', -1]
                q[9] = ['on edge', 'TEN', -1]
                q[10] = ['grouchy', 'ANG', -1]
                q[11] = ['ashamed', 'ERA', -2]
                q[12] = ['energetic', 'VIG', -1]
                q[13] = ['hopeless', 'DEP', -1]
                q[14] = ['uneasy', 'TEN', -1]
                q[15] = ['restless', 'TEN', -1]
                q[16] = ['cant concentrate', 'CON', -1]
                q[17] = ['fatigued', 'FAT', -1]
                q[18] = ['competent', 'ERA', -1]
                q[19] = ['annoyed', 'ANG', -1]
                q[20] = ['discouraged', 'DEP', -1]
                q[21] = ['resentful', 'ANG', -1]
                q[22] = ['nervous', 'TEN', -1]
                q[23] = ['miserable', 'DEP', -1]
                q[24] = ['confident', 'ERA', -1]
                q[25] = ['bitter', 'ANG', -1]
                q[26] = ['exhausted', 'FAT', -1]
                q[27] = ['anxious', 'TEN', -1]
                q[28] = ['helpless', 'DEP', -1]
                q[29] = ['weary', 'FAT', -1]
                q[30] = ['satisified', 'ERA', -1]
                q[31] = ['bewildered', 'CON', -1]
                q[32] = ['furious', 'ANG', -1]
                q[33] = ['full of pep', 'VIG', -1]
                q[34] = ['worthless', 'DEP', -1]
                q[35] = ['forgetful', 'CON', -1]
                q[36] = ['vigorous', 'VIG', -1]
                q[37] = ['uncertain', 'CON', -1]
                q[38] = ['bushed', 'FAT', -1]
                q[39] = ['embarrassed', 'ERA', -2]

            return q

        def score():
            if self.currentWidget().choice1.isChecked():
                if self.q[self.counter][2] == -1:
                    self.scorecard[self.q[self.counter][1]] += 0
                    self.task_q.put(
                        {'task_name': 'poms_baseline', 'metrics': {1: self.q[self.counter][0], 2: 0, 3: -1, 4: -1, 5: -1, 6: -1, 7: -1}})
                else:
                    self.scorecard[self.q[self.counter][1]] += 4
                    self.task_q.put(
                        {'task_name': 'poms_baseline',
                         'metrics': {1: self.q[self.counter][0], 2: 4, 3: -1, 4: -1, 5: -1, 6: -1, 7: -1}})
                self.counter += 1
                questions()
            elif self.currentWidget().choice2.isChecked():
                if self.q[self.counter][2] == -1:
                    self.scorecard[self.q[self.counter][1]] += 1
                    self.task_q.put(
                        {'task_name': 'poms_baseline', 'metrics': {1: self.q[self.counter][0], 2: 1, 3: -1, 4: -1, 5: -1, 6: -1, 7: -1}})
                else:
                    self.scorecard[self.q[self.counter][1]] += 3
                    self.task_q.put(
                        {'task_name': 'poms_baseline',
                         'metrics': {1: self.q[self.counter][0], 2: 3, 3: -1, 4: -1, 5: -1, 6: -1, 7: -1}})
                self.counter += 1
                questions()
            elif self.currentWidget().choice3.isChecked():
                if self.q[self.counter][2] == -1:
                    self.scorecard[self.q[self.counter][1]] += 2
                    self.task_q.put(
                        {'task_name': 'poms_baseline', 'metrics': {1: self.q[self.counter][0], 2: 2, 3: -1, 4: -1, 5: -1, 6: -1, 7: -1}})
                else:
                    self.scorecard[self.q[self.counter][1]] += 2
                    self.task_q.put(
                        {'task_name': 'poms_baseline',
                         'metrics': {1: self.q[self.counter][0], 2: 2, 3: -1, 4: -1, 5: -1, 6: -1, 7: -1}})
                self.counter += 1
                questions()
            elif self.currentWidget().choice4.isChecked():
                if self.q[self.counter][2] == -1:
                    self.scorecard[self.q[self.counter][1]] += 3
                    self.task_q.put(
                        {'task_name': 'poms_baseline', 'metrics': {1: self.q[self.counter][0], 2: 3, 3: -1, 4: -1, 5: -1, 6: -1, 7: -1}})
                else:
                    self.scorecard[self.q[self.counter][1]] += 1
                    self.task_q.put(
                        {'task_name': 'poms_baseline',
                         'metrics': {1: self.q[self.counter][0], 2: 1, 3: -1, 4: -1, 5: -1, 6: -1, 7: -1}})
                self.counter += 1
                questions()
            elif self.currentWidget().choice5.isChecked():
                if self.q[self.counter][2] == -1:
                    self.scorecard[self.q[self.counter][1]] += 4
                    self.task_q.put(
                        {'task_name': 'poms_baseline', 'metrics': {1: self.q[self.counter][0], 2: 4, 3: -1, 4: -1, 5: -1, 6: -1, 7: -1}})
                else:
                    self.scorecard[self.q[self.counter][1]] += 0
                    self.task_q.put(
                        {'task_name': 'poms_baseline',
                         'metrics': {1: self.q[self.counter][0], 2: 0, 3: -1, 4: -1, 5: -1, 6: -1, 7: -1}})
                self.counter += 1
                questions()
            else:
                return

        def questions():
            if self.counter < len(self.q):
                self.entry = self.q[self.counter]

                self.addWidget(PomsQuestionnaire(self.task_q, self.entry, 'baseline'))

                self.setCurrentIndex(1)
                self.setCurrentWidget(self.widget(1))

                self.cleanStack()

                self.currentWidget().choice1.clicked.connect(score)
                self.currentWidget().choice2.clicked.connect(score)
                self.currentWidget().choice3.clicked.connect(score)
                self.currentWidget().choice4.clicked.connect(score)
                self.currentWidget().choice5.clicked.connect(score)

            else:

                self.addWidget(PomsQuestionnaire(self.task_q, 'outro', 'baseline'))

                TMD = (self.scorecard['TEN'] + self.scorecard['ANG'] + self.scorecard['CON'] + self.scorecard['FAT']
                       + self.scorecard['DEP']) - (self.scorecard['VIG'] + self.scorecard['ERA'])

                #SCORING NEEDS TO BE OUTPUT

                self.task_q.put({'task_name': 'poms_baseline', 'metrics': {1: TMD, 2: -1, 3: -1, 4: -1, 5: -1, 6: -1, 7: -1}})

                self.setCurrentIndex(1)
                self.setCurrentWidget(self.widget(1))

                self.cleanStack()

                self.currentWidget().startbtn.clicked.connect(self.setConditioningScreen)

        self.counter = 0
        self.q = init_questionnare()
        self.scorecard = {'TEN': 0, 'ANG': 0, 'VIG': 0, 'CON': 0, 'DEP': 0, 'ERA': 0, 'FAT': 0}

        self.addWidget(PomsQuestionnaire(self.task_q, 'intro', 'baseline'))

        self.task_q.put({'task_name': 'poms_baseline', 'metrics': {1: 'start', 2: -1, 3: -1, 4: -1, 5: -1, 6: -1, 7: -1}})

        self.setCurrentIndex(1)
        self.setCurrentWidget(self.widget(1))

        self.cleanStack()

        self.currentWidget().startbtn.clicked.connect(questions)

    def setConditioningScreen(self):
        self.addWidget(ConditioningScreen())

        self.task_q.put({'task_name': 'end_practice', 'metrics': {1: -1, 2: -1, 3: -1, 4: -1, 5: -1, 6: -1, 7: -1}})

        self.setCurrentIndex(1)
        self.setCurrentWidget(self.widget(1))

        self.cleanStack()

        self.currentWidget().startbtn.clicked.connect(self.setAmbienceFixation)

    def setAmbienceFixation(self):
        def enableButton():
            self.setPOMSPretest()

        #ADD AMBIENCE START HERE
        self.task_q.put({'task_name': 'ambiance_fixation', 'metrics': {1: -1, 2: -1, 3: -1, 4: -1, 5: -1, 6: -1, 7: -1}})

        self.ambiance.play(loops=10, fade_ms=3000)

        self.addWidget(StandardFixation())

        self.setCurrentIndex(1)
        self.setCurrentWidget(self.widget(1))

        self.cleanStack()
        if real:
            QTimer.singleShot(10000, enableButton)
        else:
            QTimer.singleShot(1, enableButton)

    def setPOMSPretest(self):
        # Ambience continued looping?

        def init_questionnare():
            q = {}

            q[0] = ['tense', 'TEN', -1]
            if real:
                q[1] = ['angry', 'ANG', -1]
                q[2] = ['worn out', 'FAT', -1]
                q[3] = ['unhappy', 'DEP', -1]
                q[4] = ['proud', 'ERA', -1]
                q[5] = ['lively', 'VIG', -1]
                q[6] = ['confused', 'CON', -1]
                q[7] = ['sad', 'DEP', -1]
                q[8] = ['active', 'VIG', -1]
                q[9] = ['on edge', 'TEN', -1]
                q[10] = ['grouchy', 'ANG', -1]
                q[11] = ['ashamed', 'ERA', -2]
                q[12] = ['energetic', 'VIG', -1]
                q[13] = ['hopeless', 'DEP', -1]
                q[14] = ['uneasy', 'TEN', -1]
                q[15] = ['restless', 'TEN', -1]
                q[16] = ['cant concentrate', 'CON', -1]
                q[17] = ['fatigued', 'FAT', -1]
                q[18] = ['competent', 'ERA', -1]
                q[19] = ['annoyed', 'ANG', -1]
                q[20] = ['discouraged', 'DEP', -1]
                q[21] = ['resentful', 'ANG', -1]
                q[22] = ['nervous', 'TEN', -1]
                q[23] = ['miserable', 'DEP', -1]
                q[24] = ['confident', 'ERA', -1]
                q[25] = ['bitter', 'ANG', -1]
                q[26] = ['exhausted', 'FAT', -1]
                q[27] = ['anxious', 'TEN', -1]
                q[28] = ['helpless', 'DEP', -1]
                q[29] = ['weary', 'FAT', -1]
                q[30] = ['satisified', 'ERA', -1]
                q[31] = ['bewildered', 'CON', -1]
                q[32] = ['furious', 'ANG', -1]
                q[33] = ['full of pep', 'VIG', -1]
                q[34] = ['worthless', 'DEP', -1]
                q[35] = ['forgetful', 'CON', -1]
                q[36] = ['vigorous', 'VIG', -1]
                q[37] = ['uncertain', 'CON', -1]
                q[38] = ['bushed', 'FAT', -1]
                q[39] = ['embarrassed', 'ERA', -2]

            return q

        def score():
            if self.currentWidget().choice1.isChecked():
                if self.q[self.counter][2] == -1:
                    self.scorecard[self.q[self.counter][1]] += 0
                    self.task_q.put(
                        {'task_name': 'poms_baseline', 'metrics': {1: self.q[self.counter][0], 2: 0, 3: -1, 4: -1, 5: -1, 6: -1, 7: -1}})
                else:
                    self.scorecard[self.q[self.counter][1]] += 4
                    self.task_q.put(
                        {'task_name': 'poms_baseline',
                         'metrics': {1: self.q[self.counter][0], 2: 4, 3: -1, 4: -1, 5: -1, 6: -1, 7: -1}})
                self.counter += 1
                questions()
            elif self.currentWidget().choice2.isChecked():
                if self.q[self.counter][2] == -1:
                    self.scorecard[self.q[self.counter][1]] += 1
                    self.task_q.put(
                        {'task_name': 'poms_baseline', 'metrics': {1: self.q[self.counter][0], 2: 1, 3: -1, 4: -1, 5: -1, 6: -1, 7: -1}})
                else:
                    self.scorecard[self.q[self.counter][1]] += 3
                    self.task_q.put(
                        {'task_name': 'poms_baseline',
                         'metrics': {1: self.q[self.counter][0], 2: 3, 3: -1, 4: -1, 5: -1, 6: -1, 7: -1}})
                self.counter += 1
                questions()
            elif self.currentWidget().choice3.isChecked():
                if self.q[self.counter][2] == -1:
                    self.scorecard[self.q[self.counter][1]] += 2
                    self.task_q.put(
                        {'task_name': 'poms_baseline', 'metrics': {1: self.q[self.counter][0], 2: 2, 3: -1, 4: -1, 5: -1, 6: -1, 7: -1}})
                else:
                    self.scorecard[self.q[self.counter][1]] += 2
                    self.task_q.put(
                        {'task_name': 'poms_baseline',
                         'metrics': {1: self.q[self.counter][0], 2: 2, 3: -1, 4: -1, 5: -1, 6: -1, 7: -1}})
                self.counter += 1
                questions()
            elif self.currentWidget().choice4.isChecked():
                if self.q[self.counter][2] == -1:
                    self.scorecard[self.q[self.counter][1]] += 3
                    self.task_q.put(
                        {'task_name': 'poms_baseline', 'metrics': {1: self.q[self.counter][0], 2: 3, 3: -1, 4: -1, 5: -1, 6: -1, 7: -1}})
                else:
                    self.scorecard[self.q[self.counter][1]] += 1
                    self.task_q.put(
                        {'task_name': 'poms_baseline',
                         'metrics': {1: self.q[self.counter][0], 2: 1, 3: -1, 4: -1, 5: -1, 6: -1, 7: -1}})
                self.counter += 1
                questions()
            elif self.currentWidget().choice5.isChecked():
                if self.q[self.counter][2] == -1:
                    self.scorecard[self.q[self.counter][1]] += 4
                    self.task_q.put(
                        {'task_name': 'poms_baseline', 'metrics': {1: self.q[self.counter][0], 2: 4, 3: -1, 4: -1, 5: -1, 6: -1, 7: -1}})
                else:
                    self.scorecard[self.q[self.counter][1]] += 0
                    self.task_q.put(
                        {'task_name': 'poms_baseline',
                         'metrics': {1: self.q[self.counter][0], 2: 0, 3: -1, 4: -1, 5: -1, 6: -1, 7: -1}})
                self.counter += 1
                questions()
            else:
                return

        def questions():
            if self.counter < len(self.q):
                self.entry = self.q[self.counter]

                self.addWidget(PomsQuestionnaire(self.task_q, self.entry, 'pre'))

                self.setCurrentIndex(1)
                self.setCurrentWidget(self.widget(1))

                self.cleanStack()

                self.currentWidget().choice1.clicked.connect(score)
                self.currentWidget().choice2.clicked.connect(score)
                self.currentWidget().choice3.clicked.connect(score)
                self.currentWidget().choice4.clicked.connect(score)
                self.currentWidget().choice5.clicked.connect(score)

            else:

                self.addWidget(PomsQuestionnaire(self.task_q, 'outro', 'pre'))

                TMD = (self.scorecard['TEN'] + self.scorecard['ANG'] + self.scorecard['CON'] + self.scorecard['FAT']
                       + self.scorecard['DEP']) - (self.scorecard['VIG'] + self.scorecard['ERA'])

                #SCORING NEEDS TO BE OUTPUT

                self.task_q.put({'task_name': 'poms_pretest', 'metrics': {1: TMD, 2: -1, 3: -1, 4: -1, 5: -1, 6: -1, 7: -1}})

                self.setCurrentIndex(1)
                self.setCurrentWidget(self.widget(1))

                self.cleanStack()

                self.currentWidget().startbtn.clicked.connect(self.setIntroFixation)

        self.counter = 0
        self.q = init_questionnare()
        self.scorecard = {'TEN': 0, 'ANG': 0, 'VIG': 0, 'CON': 0, 'DEP': 0, 'ERA': 0, 'FAT': 0}

        self.addWidget(PomsQuestionnaire(self.task_q, 'intro', 'pre'))

        self.task_q.put({'task_name': 'poms_pretest', 'metrics': {1: 'start', 2: -1, 3: -1, 4: -1, 5: -1, 6: -1, 7: -1}})


        self.setCurrentIndex(1)
        self.setCurrentWidget(self.widget(1))

        self.cleanStack()

        self.currentWidget().startbtn.clicked.connect(questions)

    def setIntroFixation(self):
        def enableButton():
            self.intro.fadeout(3000)
            self.beat_end_flag = True
            self.setSession()

        def playBeat():
            print("Playing beat")
            self.beat.play()
            if not self.beat_end_flag:
                QTimer.singleShot(self.play_rate * 1000, playBeat)

        def adjustRate():
            print("adjusting")
            if self.play_rate < self.goal_rate:
                self.play_rate += self.increase_per_second
                QTimer.singleShot(1000, adjustRate)

        # INTRO FIXATIeeON
        self.ambiance.fadeout(500)

        if self.intro is not None:
            if self.condition == 4:
                self.beat_end_flag = False
                self.play_rate = 1 / (120/60)
                self.goal_rate = 1 / (75/60)
                self.increase_per_second = (self.goal_rate - self.play_rate) / 15

                QTimer.singleShot(self.play_rate * 1000, playBeat)
                QTimer.singleShot(1000, adjustRate)

            self.intro.play(fade_ms=500)
            length = self.intro.get_length()*1000
            if real:
                QTimer.singleShot(length, enableButton)
            else:
                QTimer.singleShot(1, enableButton)

        else:
            self.intro = self.ambiance
            self.intro.play(fade_ms=500)
            if real:
                QTimer.singleShot(32000, enableButton)
            else:
                QTimer.singleShot(1, enableButton)

        self.addWidget(StandardFixation())

        self.task_q.put({'task_name': 'intro_fixation', 'metrics': {1: -1, 2: -1, 3: -1, 4: -1, 5: -1, 6: -1, 7: -1}})

        self.setCurrentIndex(1)
        self.setCurrentWidget(self.widget(1))

        self.cleanStack()

    def setSession(self):
        self.addWidget(Session())
        self.task_q.put({'task_name': 'session', 'metrics': {1: 'start', 2: -1, 3: -1, 4: -1, 5: -1, 6: -1, 7: -1}})

        self.setCurrentIndex(1)
        self.setCurrentWidget(self.widget(1))

        self.cleanStack()

        self.body.play(fade_ms=500, loops=30)

        tasks = ['pong', 'wcst', 'driving']
        for i in range(0, 3):
            print(tasks)
            selection = random.randint(0, len(tasks)-1)

            if tasks[selection] == 'wcst':
                self.task_q.put({'task_name': 'session_wcst', 'metrics': {1: 'start', 2: -1, 3: -1, 4: -1, 5: -1, 6: -1, 7: -1}})

                print('wcst')
                wcst = WisconsinCardSort(self.task_q, self.bio_q_algo, self.condition, 2000, 'experiment', 'experiment')
                del wcst

            elif tasks[selection] == 'driving':
                self.task_q.put({'task_name': 'session_driving', 'metrics': {1: 'start', 2: -1, 3: -1, 4: -1, 5: -1, 6: -1, 7: -1}})

                print('driving')
                driving = DrivingGame(self.task_q, self.bio_q_algo, self.condition, 'experiment')
                del driving


            elif tasks[selection] == 'pong':
                self.task_q.put({'task_name': 'session_pong', 'metrics': {1: 'start', 2: -1, 3: -1, 4: -1, 5: -1, 6: -1, 7: -1}})

                print('pong')

                pong = PongGame(self.task_q, self.bio_q_algo, self.condition, 'experiment')
                del pong

            tasks.remove(tasks[selection])

        self.setAmbientPrimePost()

    def setAmbientPrimePost(self):
        self.addWidget(AmbientPrimePost(self.task_q, self.participant_id, self.condition))

        self.task_q.put({'task_name': 'ambient_prime_post', 'metrics': {1: 'start', 2: -1, 3: -1, 4: -1, 5: -1, 6: -1, 7: -1}})


        self.setCurrentIndex(1)
        self.setCurrentWidget(self.widget(1))

        self.cleanStack()

        self.currentWidget().startbtn.clicked.connect(self.setOutroFixation)

    def setOutroFixation(self):
        def enableButton():
            self.outro.fadeout(500)
            self.setAmbienceFixationPost()

        self.body.fadeout(500)

        if self.outro is not None:
            self.outro.play(fade_ms=500)
            if real:
                QTimer.singleShot(self.outro.get_length()*1000, enableButton)
            else:
                QTimer.singleShot(1, enableButton)

        else:
            self.outro = self.body
            self.outro.play(fade_ms=500)
            if real:
                QTimer.singleShot(10000, enableButton)
            else:
                QTimer.singleShot(1, enableButton)

        self.addWidget(StandardFixation())

        self.task_q.put({'task_name': 'outro_fixation', 'metrics': {1: 'start', 2: -1, 3: -1, 4: -1, 5: -1, 6: -1, 7: -1}})


        self.setCurrentIndex(1)
        self.setCurrentWidget(self.widget(1))

        self.cleanStack()

    def setAmbienceFixationPost(self):
        def enableButton():
            self.setPOMSPosttest()

        self.ambiance.play(loops=20)

        self.addWidget(StandardFixation())

        self.task_q.put({'task_name': 'ambience_fixation', 'metrics': {1: 'start', 2: -1, 3: -1, 4: -1, 5: -1, 6: -1, 7: -1}})

        self.setCurrentIndex(1)
        self.setCurrentWidget(self.widget(1))

        self.cleanStack()
        if real:
            QTimer.singleShot(10000, enableButton)
        else:
            QTimer.singleShot(1, enableButton)

    def setPOMSPosttest(self):
        def init_questionnare():
            q = {}

            q[0] = ['tense', 'TEN', -1]
            if real:
                q[1] = ['angry', 'ANG', -1]
                q[2] = ['worn out', 'FAT', -1]
                q[3] = ['unhappy', 'DEP', -1]
                q[4] = ['proud', 'ERA', -1]
                q[5] = ['lively', 'VIG', -1]
                q[6] = ['confused', 'CON', -1]
                q[7] = ['sad', 'DEP', -1]
                q[8] = ['active', 'VIG', -1]
                q[9] = ['on edge', 'TEN', -1]
                q[10] = ['grouchy', 'ANG', -1]
                q[11] = ['ashamed', 'ERA', -2]
                q[12] = ['energetic', 'VIG', -1]
                q[13] = ['hopeless', 'DEP', -1]
                q[14] = ['uneasy', 'TEN', -1]
                q[15] = ['restless', 'TEN', -1]
                q[16] = ['cant concentrate', 'CON', -1]
                q[17] = ['fatigued', 'FAT', -1]
                q[18] = ['competent', 'ERA', -1]
                q[19] = ['annoyed', 'ANG', -1]
                q[20] = ['discouraged', 'DEP', -1]
                q[21] = ['resentful', 'ANG', -1]
                q[22] = ['nervous', 'TEN', -1]
                q[23] = ['miserable', 'DEP', -1]
                q[24] = ['confident', 'ERA', -1]
                q[25] = ['bitter', 'ANG', -1]
                q[26] = ['exhausted', 'FAT', -1]
                q[27] = ['anxious', 'TEN', -1]
                q[28] = ['helpless', 'DEP', -1]
                q[29] = ['weary', 'FAT', -1]
                q[30] = ['satisified', 'ERA', -1]
                q[31] = ['bewildered', 'CON', -1]
                q[32] = ['furious', 'ANG', -1]
                q[33] = ['full of pep', 'VIG', -1]
                q[34] = ['worthless', 'DEP', -1]
                q[35] = ['forgetful', 'CON', -1]
                q[36] = ['vigorous', 'VIG', -1]
                q[37] = ['uncertain', 'CON', -1]
                q[38] = ['bushed', 'FAT', -1]
                q[39] = ['embarrassed', 'ERA', -2]

            return q

        def score():
            if self.currentWidget().choice1.isChecked():
                if self.q[self.counter][2] == -1:
                    self.scorecard[self.q[self.counter][1]] += 0
                    self.task_q.put(
                        {'task_name': 'poms_posttest', 'metrics': {1: self.q[self.counter][0], 2: 0, 3: -1, 4: -1, 5: -1, 6: -1, 7: -1}})
                else:
                    self.scorecard[self.q[self.counter][1]] += 4
                    self.task_q.put(
                        {'task_name': 'poms_posttest',
                         'metrics': {1: self.q[self.counter][0], 2: 4, 3: -1, 4: -1, 5: -1, 6: -1, 7: -1}})
                self.counter += 1
                questions()
            elif self.currentWidget().choice2.isChecked():
                if self.q[self.counter][2] == -1:
                    self.scorecard[self.q[self.counter][1]] += 1
                    self.task_q.put(
                        {'task_name': 'poms_posttest', 'metrics': {1: self.q[self.counter][0], 2: 1, 3: -1, 4: -1, 5: -1, 6: -1, 7: -1}})
                else:
                    self.scorecard[self.q[self.counter][1]] += 3
                    self.task_q.put(
                        {'task_name': 'poms_posttest',
                         'metrics': {1: self.q[self.counter][0], 2: 3, 3: -1, 4: -1, 5: -1, 6: -1, 7: -1}})
                self.counter += 1
                questions()
            elif self.currentWidget().choice3.isChecked():
                if self.q[self.counter][2] == -1:
                    self.scorecard[self.q[self.counter][1]] += 2
                    self.task_q.put(
                        {'task_name': 'poms_posttest', 'metrics': {1: self.q[self.counter][0], 2: 2, 3: -1, 4: -1, 5: -1, 6: -1, 7: -1}})
                else:
                    self.scorecard[self.q[self.counter][1]] += 2
                    self.task_q.put(
                        {'task_name': 'poms_posttest',
                         'metrics': {1: self.q[self.counter][0], 2: 2, 3: -1, 4: -1, 5: -1, 6: -1, 7: -1}})
                self.counter += 1
                questions()
            elif self.currentWidget().choice4.isChecked():
                if self.q[self.counter][2] == -1:
                    self.scorecard[self.q[self.counter][1]] += 3
                    self.task_q.put(
                        {'task_name': 'poms_posttest', 'metrics': {1: self.q[self.counter][0], 2: 3, 3: -1, 4: -1, 5: -1, 6: -1, 7: -1}})
                else:
                    self.scorecard[self.q[self.counter][1]] += 1
                    self.task_q.put(
                        {'task_name': 'poms_posttest',
                         'metrics': {1: self.q[self.counter][0], 2: 1, 3: -1, 4: -1, 5: -1, 6: -1, 7: -1}})
                self.counter += 1
                questions()
            elif self.currentWidget().choice5.isChecked():
                if self.q[self.counter][2] == -1:
                    self.scorecard[self.q[self.counter][1]] += 4
                    self.task_q.put(
                        {'task_name': 'poms_posttest', 'metrics': {1: self.q[self.counter][0], 2: 4, 3: -1, 4: -1, 5: -1, 6: -1, 7: -1}})
                else:
                    self.scorecard[self.q[self.counter][1]] += 0
                    self.task_q.put(
                        {'task_name': 'poms_posttest',
                         'metrics': {1: self.q[self.counter][0], 2: 0, 3: -1, 4: -1, 5: -1, 6: -1, 7: -1}})
                self.counter += 1
                questions()
            else:
                return

        def questions():
            if self.counter < len(self.q):
                self.entry = self.q[self.counter]

                self.addWidget(PomsQuestionnaire(self.task_q, self.entry, 'post'))

                self.setCurrentIndex(1)
                self.setCurrentWidget(self.widget(1))

                self.cleanStack()

                self.currentWidget().choice1.clicked.connect(score)
                self.currentWidget().choice2.clicked.connect(score)
                self.currentWidget().choice3.clicked.connect(score)
                self.currentWidget().choice4.clicked.connect(score)
                self.currentWidget().choice5.clicked.connect(score)

            else:

                self.addWidget(PomsQuestionnaire(self.task_q, 'outro', 'post'))

                TMD = (self.scorecard['TEN'] + self.scorecard['ANG'] + self.scorecard['CON'] + self.scorecard['FAT']
                       + self.scorecard['DEP']) - (self.scorecard['VIG'] + self.scorecard['ERA'])

                #SCORING NEEDS TO BE OUTPUT

                self.task_q.put({'task_name': 'poms_posttest', 'metrics': {1: TMD, 2: -1, 3: -1, 4: -1, 5: -1, 6: -1, 7: -1}})

                self.setCurrentIndex(1)
                self.setCurrentWidget(self.widget(1))

                self.cleanStack()

                self.currentWidget().startbtn.clicked.connect(self.setAmbienceFixationEnd)

        self.counter = 0
        self.q = init_questionnare()
        self.scorecard = {'TEN': 0, 'ANG': 0, 'VIG': 0, 'CON': 0, 'DEP': 0, 'ERA': 0, 'FAT': 0}

        self.addWidget(PomsQuestionnaire(self.task_q, 'intro', 'post'))

        self.task_q.put({'task_name': 'poms_posttest', 'metrics': {1: 'start', 2: -1, 3: -1, 4: -1, 5: -1, 6: -1, 7: -1}})


        self.setCurrentIndex(1)
        self.setCurrentWidget(self.widget(1))

        self.cleanStack()

        self.currentWidget().startbtn.clicked.connect(questions)

    def setAmbienceFixationEnd(self):
        def enableButton():
            self.ambiance.fadeout(3000)
            if self.final_poms:
                self.setPOMSFinal()
            else:
                self.setEnd()

        self.addWidget(StandardFixation())

        self.task_q.put({'task_name': 'ambience_fixation_end', 'metrics': {1: 'start', 2: -1, 3: -1, 4: -1, 5: -1, 6: -1, 7: -1}})

        self.setCurrentIndex(1)
        self.setCurrentWidget(self.widget(1))

        self.cleanStack()
        if real:
            QTimer.singleShot(10000, enableButton)
        else:
            QTimer.singleShot(1, enableButton)

    def setPOMSFinal(self):
        def init_questionnare():
            q = {}

            q[0] = ['tense', 'TEN', -1]
            if real:
                q[1] = ['angry', 'ANG', -1]
                q[2] = ['worn out', 'FAT', -1]
                q[3] = ['unhappy', 'DEP', -1]
                q[4] = ['proud', 'ERA', -1]
                q[5] = ['lively', 'VIG', -1]
                q[6] = ['confused', 'CON', -1]
                q[7] = ['sad', 'DEP', -1]
                q[8] = ['active', 'VIG', -1]
                q[9] = ['on edge', 'TEN', -1]
                q[10] = ['grouchy', 'ANG', -1]
                q[11] = ['ashamed', 'ERA', -2]
                q[12] = ['energetic', 'VIG', -1]
                q[13] = ['hopeless', 'DEP', -1]
                q[14] = ['uneasy', 'TEN', -1]
                q[15] = ['restless', 'TEN', -1]
                q[16] = ['cant concentrate', 'CON', -1]
                q[17] = ['fatigued', 'FAT', -1]
                q[18] = ['competent', 'ERA', -1]
                q[19] = ['annoyed', 'ANG', -1]
                q[20] = ['discouraged', 'DEP', -1]
                q[21] = ['resentful', 'ANG', -1]
                q[22] = ['nervous', 'TEN', -1]
                q[23] = ['miserable', 'DEP', -1]
                q[24] = ['confident', 'ERA', -1]
                q[25] = ['bitter', 'ANG', -1]
                q[26] = ['exhausted', 'FAT', -1]
                q[27] = ['anxious', 'TEN', -1]
                q[28] = ['helpless', 'DEP', -1]
                q[29] = ['weary', 'FAT', -1]
                q[30] = ['satisified', 'ERA', -1]
                q[31] = ['bewildered', 'CON', -1]
                q[32] = ['furious', 'ANG', -1]
                q[33] = ['full of pep', 'VIG', -1]
                q[34] = ['worthless', 'DEP', -1]
                q[35] = ['forgetful', 'CON', -1]
                q[36] = ['vigorous', 'VIG', -1]
                q[37] = ['uncertain', 'CON', -1]
                q[38] = ['bushed', 'FAT', -1]
                q[39] = ['embarrassed', 'ERA', -2]

            return q

        def score():
            if self.currentWidget().choice1.isChecked():
                if self.q[self.counter][2] == -1:
                    self.scorecard[self.q[self.counter][1]] += 0
                    self.task_q.put(
                        {'task_name': 'poms_final',
                         'metrics': {1: self.q[self.counter][0], 2: 0, 3: -1, 4: -1, 5: -1, 6: -1, 7: -1}})
                else:
                    self.scorecard[self.q[self.counter][1]] += 4
                    self.task_q.put(
                        {'task_name': 'poms_final',
                         'metrics': {1: self.q[self.counter][0], 2: 4, 3: -1, 4: -1, 5: -1, 6: -1, 7: -1}})
                self.counter += 1
                questions()
            elif self.currentWidget().choice2.isChecked():
                if self.q[self.counter][2] == -1:
                    self.scorecard[self.q[self.counter][1]] += 1
                    self.task_q.put(
                        {'task_name': 'poms_final',
                         'metrics': {1: self.q[self.counter][0], 2: 1, 3: -1, 4: -1, 5: -1, 6: -1, 7: -1}})
                else:
                    self.scorecard[self.q[self.counter][1]] += 3
                    self.task_q.put(
                        {'task_name': 'poms_final',
                         'metrics': {1: self.q[self.counter][0], 2: 3, 3: -1, 4: -1, 5: -1, 6: -1, 7: -1}})
                self.counter += 1
                questions()
            elif self.currentWidget().choice3.isChecked():
                if self.q[self.counter][2] == -1:
                    self.scorecard[self.q[self.counter][1]] += 2
                    self.task_q.put(
                        {'task_name': 'poms_final',
                         'metrics': {1: self.q[self.counter][0], 2: 2, 3: -1, 4: -1, 5: -1, 6: -1, 7: -1}})
                else:
                    self.scorecard[self.q[self.counter][1]] += 2
                    self.task_q.put(
                        {'task_name': 'poms_final',
                         'metrics': {1: self.q[self.counter][0], 2: 2, 3: -1, 4: -1, 5: -1, 6: -1, 7: -1}})
                self.counter += 1
                questions()
            elif self.currentWidget().choice4.isChecked():
                if self.q[self.counter][2] == -1:
                    self.scorecard[self.q[self.counter][1]] += 3
                    self.task_q.put(
                        {'task_name': 'poms_final',
                         'metrics': {1: self.q[self.counter][0], 2: 3, 3: -1, 4: -1, 5: -1, 6: -1, 7: -1}})
                else:
                    self.scorecard[self.q[self.counter][1]] += 1
                    self.task_q.put(
                        {'task_name': 'poms_final',
                         'metrics': {1: self.q[self.counter][0], 2: 1, 3: -1, 4: -1, 5: -1, 6: -1, 7: -1}})
                self.counter += 1
                questions()
            elif self.currentWidget().choice5.isChecked():
                if self.q[self.counter][2] == -1:
                    self.scorecard[self.q[self.counter][1]] += 4
                    self.task_q.put(
                        {'task_name': 'poms_final',
                         'metrics': {1: self.q[self.counter][0], 2: 4, 3: -1, 4: -1, 5: -1, 6: -1, 7: -1}})
                else:
                    self.scorecard[self.q[self.counter][1]] += 0
                    self.task_q.put(
                        {'task_name': 'poms_final',
                         'metrics': {1: self.q[self.counter][0], 2: 0, 3: -1, 4: -1, 5: -1, 6: -1, 7: -1}})
                self.counter += 1
                questions()
            else:
                return

        def questions():
            if self.counter < len(self.q):
                self.entry = self.q[self.counter]

                self.addWidget(PomsQuestionnaire(self.task_q, self.entry, 'baseline'))

                self.setCurrentIndex(1)
                self.setCurrentWidget(self.widget(1))

                self.cleanStack()

                self.currentWidget().choice1.clicked.connect(score)
                self.currentWidget().choice2.clicked.connect(score)
                self.currentWidget().choice3.clicked.connect(score)
                self.currentWidget().choice4.clicked.connect(score)
                self.currentWidget().choice5.clicked.connect(score)

            else:

                self.addWidget(PomsQuestionnaire(self.task_q, 'outro', 'post'))

                TMD = (self.scorecard['TEN'] + self.scorecard['ANG'] + self.scorecard['CON'] + self.scorecard['FAT']
                       + self.scorecard['DEP']) - (self.scorecard['VIG'] + self.scorecard['ERA'])

                # SCORING NEEDS TO BE OUTPUT

                self.task_q.put(
                    {'task_name': 'poms_final', 'metrics': {1: TMD, 2: -1, 3: -1, 4: -1, 5: -1, 6: -1, 7: -1}})

                self.setCurrentIndex(1)
                self.setCurrentWidget(self.widget(1))

                self.cleanStack()

                self.currentWidget().startbtn.clicked.connect(self.setEnd)

        self.counter = 0
        self.q = init_questionnare()
        self.scorecard = {'TEN': 0, 'ANG': 0, 'VIG': 0, 'CON': 0, 'DEP': 0, 'ERA': 0, 'FAT': 0}

        self.addWidget(PomsQuestionnaire(self.task_q, 'intro', 'post'))

        self.task_q.put(
            {'task_name': 'poms_final', 'metrics': {1: 'start', 2: -1, 3: -1, 4: -1, 5: -1, 6: -1, 7: -1}})

        self.setCurrentIndex(1)
        self.setCurrentWidget(self.widget(1))

        self.cleanStack()

        self.currentWidget().startbtn.clicked.connect(questions)

    def setEnd(self):
        self.addWidget(End())

        self.task_q.put({'task_name': 'end', 'metrics': {1: 'end', 2: -1, 3: -1, 4: -1, 5: -1, 6: -1, 7: -1}})

        self.setCurrentIndex(1)
        self.setCurrentWidget(self.widget(1))

        self.cleanStack()







if __name__ == '__main__':
    app = QApplication([])
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())

    window = QWidget()

    stack = ProductiveStackFlow(condition=1, participant_id=3)

    stack.setSelectionPage()

    layout = QGridLayout(window)
    layout.addWidget(stack, 0, 0, 1, 1)


    window.showFullScreen()

    sys.exit(app.exec_())


# class CreativeStackFlow(QStackedWidget):
#
#     def __init__(self, condition, participant_id, parent=None):
#         QStackedWidget.__init__(self, parent)
#         self.setGeometry(0, 0, 1920, 1080)
#
#         self.participant_id = participant_id
#         self.condition = condition
#         self.cur_index = 0
#         self.task_q = Queue()
#         self.bio_q = Queue()
#         self.bio_q_algo = Queue()
#
#         self.task_q.put({'task_name': 'start', 'metrics': {1: 'start', 2: -1, 3: -1, 4: -1, 5: -1, 6: -1, 7: -1}})
#
#         pygame.init()
#         pygame.mixer.init()
#
#         if real:
#             threading.Thread(name="Biometrics Tracker", target=self.startBiometrics).start()
#             threading.Thread(name="Data Logger", target=self.startDataLogger).start()
#
#         self.ambiance = pygame.mixer.Sound("soundscapes/Brody_Office_Ambience_Loop_1.ogg")
#
#         if condition == 1:
#             self.intro = pygame.mixer.Sound("soundscapes/1_BRODY_SONIC_JOURNEY_v2_ENTRAINMENT.ogg")
#             self.body = pygame.mixer.Sound("soundscapes/1_BRODY_SONIC_JOURNEY_v2_MAIN_MUSIC_SD_BIN_PULSE80.ogg")
#             self.outro = pygame.mixer.Sound("soundscapes/1_BRODY_SONIC_JOURNEY_v2_RETURN.ogg")
#         elif condition == 2:
#             self.intro = pygame.mixer.Sound("soundscapes/2_BRODY_STOCK_INTRO.ogg")
#             self.body = pygame.mixer.Sound("soundscapes/2_BRODY_STOCK EQUIVALENT.ogg")
#             self.outro = pygame.mixer.Sound("soundscapes/2_BRODY_STOCK_RETURN.ogg")
#         elif condition == 3:
#             print("OFFICE AMBIENCE")
#             self.intro = None
#             self.body = self.ambiance
#             self.outro = None
#         elif condition == 4:
#             self.intro = pygame.mixer.Sound("soundscapes/4_BRODY_SONIC_JOURNEY_v2_ENTRAINMENT_DYNAMIC.ogg")
#             self.body = pygame.mixer.Sound("soundscapes/4_BRODY_SONIC_JOURNEY_v2_MAIN_DYNAMIC.ogg")
#             self.outro = pygame.mixer.Sound("soundscapes/4_BRODY_SONIC_JOURNEY_v2_RETURN DYNAMIC.ogg")
#             self.beat = pygame.mixer.Sound("soundscapes/4_BRODY_SONIC_JOURNEY_v2_SINGLE_BEAT_DYNAMIC.ogg")
#
#     def setCurrentIndex(self, index):
#         self.fader_widget = FaderWidget(self.currentWidget(), self.widget(index))
#         QStackedWidget.setCurrentIndex(self, index)
#
#     def keyPressEvent(self, e):
#         if e.key() == Qt.Key_Escape:
#             sys.exit()
#
#     def startBiometrics(self):
#         self.eye_tracker = BiometricTracking(self.bio_q, self.bio_q_algo)
#
#     def startDataLogger(self):
#         self.data_logger = DataLogger(self.bio_q, self.task_q, self.participant_id, self.condition)
#
#     def cleanStack(self):
#         print("cleaning!")
#         widget = self.widget(0)
#         self.removeWidget(widget)
#         widget.setParent(None)
#         # self.widget(0).setParent(None)
#         # self.widget(0).deleteLater()
#         # self.removeWidget(self.widget(0))
#
#     def setSelectionPage(self):
#         def cond1():
#             self.condition = 1
#         def cond2():
#             self.condition = 2
#         def cond3():
#             self.condition = 3
#         def cond4():
#             self.condition = 4
#         def exper():
#             self.practice = False
#         def prac():
#             self.practice = True
#         def update():
#             if self.condition == 1:
#                 self.intro = pygame.mixer.Sound("soundscapes/1_BRODY_SONIC_JOURNEY_v2_ENTRAINMENT.ogg")
#                 self.body = pygame.mixer.Sound("soundscapes/1_BRODY_SONIC_JOURNEY_v2_MAIN_MUSIC_SD_BIN_PULSE80.ogg")
#                 self.outro = pygame.mixer.Sound("soundscapes/1_BRODY_SONIC_JOURNEY_v2_RETURN.ogg")
#             elif self.condition == 2:
#                 self.intro = pygame.mixer.Sound("soundscapes/2_BRODY_STOCK_INTRO.ogg")
#                 self.body = pygame.mixer.Sound("soundscapes/2_BRODY_STOCK EQUIVALENT.ogg")
#                 self.outro = pygame.mixer.Sound("soundscapes/2_BRODY_STOCK_RETURN.ogg")
#             elif self.condition == 3:
#                 print("OFFICE AMBIANCE")
#                 self.intro = None
#                 self.body = self.ambiance
#                 self.outro = None
#             elif self.condition == 4:
#                 self.intro = pygame.mixer.Sound("soundscapes/4_BRODY_SONIC_JOURNEY_v2_ENTRAINMENT_DYNAMIC.ogg")
#                 self.body = pygame.mixer.Sound("soundscapes/4_BRODY_SONIC_JOURNEY_v2_MAIN_DYNAMIC.ogg")
#                 self.outro = pygame.mixer.Sound("soundscapes/4_BRODY_SONIC_JOURNEY_v2_RETURN DYNAMIC.ogg")
#                 self.beat = pygame.mixer.Sound("soundscapes/4_BRODY_SONIC_JOURNEY_v2_SINGLE_BEAT_DYNAMIC.ogg")
#
#             self.setStartPage()
#
#         self.task_q.put({'task_name': 'selection_page', 'metrics': {1: -1, 2: -1, 3: -1, 4: -1, 5: -1, 6: -1, 7: -1}})
#
#         self.addWidget(SelectionPage())
#
#         self.setCurrentWidget(self.widget(0))
#
#         self.currentWidget().cond1.clicked.connect(cond1)
#         self.currentWidget().cond2.clicked.connect(cond2)
#         self.currentWidget().cond3.clicked.connect(cond3)
#         self.currentWidget().cond4.clicked.connect(cond4)
#
#         self.currentWidget().prac.clicked.connect(prac)
#         self.currentWidget().exper.clicked.connect(exper)
#         print(self.currentWidget())
#
#         self.currentWidget().startButton.clicked.connect(update)
#
#     def setStartPage(self):
#         self.task_q.put({'task_name': 'start_page', 'metrics': {1: -1, 2: -1, 3: -1, 4: -1, 5: -1, 6: -1, 7: -1}})
#
#         self.addWidget(StartPage())
#
#         self.setCurrentIndex(1)
#         self.setCurrentWidget(self.widget(1))
#
#         self.cleanStack()
#         if self.practice:
#             self.currentWidget().startButton.clicked.connect(self.setInitFixation)
#         else:
#             self.currentWidget().startButton.clicked.connect(self.setAmbienceFixation)
#
#     def setInitFixation(self):
#         self.setPOMSPretest()
#
#     def setAmbienceFixation(self):
#         self.setPOMSPretest()
#
#     def setPOMSPretest(self):
#         # Ambience continued looping?
#
#         def init_questionnare():
#             q = {}
#
#             q[0] = ['tense', 'TEN', -1]
#             if real:
#                 q[1] = ['angry', 'ANG', -1]
#                 q[2] = ['worn out', 'FAT', -1]
#                 q[3] = ['unhappy', 'DEP', -1]
#                 q[4] = ['proud', 'ERA', -1]
#                 q[5] = ['lively', 'VIG', -1]
#                 q[6] = ['confused', 'CON', -1]
#                 q[7] = ['sad', 'DEP', -1]
#                 q[8] = ['active', 'VIG', -1]
#                 q[9] = ['on edge', 'TEN', -1]
#                 q[10] = ['grouchy', 'ANG', -1]
#                 q[11] = ['ashamed', 'ERA', -2]
#                 q[12] = ['energetic', 'VIG', -1]
#                 q[13] = ['hopeless', 'DEP', -1]
#                 q[14] = ['uneasy', 'TEN', -1]
#                 q[15] = ['restless', 'TEN', -1]
#                 q[16] = ['cant concentrate', 'CON', -1]
#                 q[17] = ['fatigued', 'FAT', -1]
#                 q[18] = ['competent', 'ERA', -1]
#                 q[19] = ['annoyed', 'ANG', -1]
#                 q[20] = ['discourage', 'DEP', -1]
#                 q[21] = ['resentful', 'ANG', -1]
#                 q[22] = ['nervous', 'TEN', -1]
#                 q[23] = ['miserable', 'DEP', -1]
#                 q[24] = ['confident', 'ERA', -1]
#                 q[25] = ['bitter', 'ANG', -1]
#                 q[26] = ['exhausted', 'FAT', -1]
#                 q[27] = ['anxious', 'TEN', -1]
#                 q[28] = ['helpless', 'DEP', -1]
#                 q[29] = ['weary', 'FAT', -1]
#                 q[30] = ['satisified', 'ERA', -1]
#                 q[31] = ['bewildered', 'CON', -1]
#                 q[32] = ['furious', 'ANG', -1]
#                 q[33] = ['full of pep', 'VIG', -1]
#                 q[34] = ['worthless', 'DEP', -1]
#                 q[35] = ['forgetful', 'CON', -1]
#                 q[36] = ['vigorous', 'VIG', -1]
#                 q[37] = ['uncertain', 'CON', -1]
#                 q[38] = ['bushed', 'FAT', -1]
#                 q[39] = ['embarrassed', 'ERA', -2]
#
#             return q
#
#         def score():
#             if self.currentWidget().choice1.isChecked():
#                 if self.q[self.counter][2] == -1:
#                     self.scorecard[self.q[self.counter][1]] += 0
#                     self.task_q.put(
#                         {'task_name': 'poms_baseline', 'metrics': {1: self.q[self.counter][0], 2: 0, 3: -1, 4: -1, 5: -1, 6: -1, 7: -1}})
#                 else:
#                     self.scorecard[self.q[self.counter][1]] += 4
#                     self.task_q.put(
#                         {'task_name': 'poms_baseline',
#                          'metrics': {1: self.q[self.counter][0], 2: 4, 3: -1, 4: -1, 5: -1, 6: -1, 7: -1}})
#                 self.counter += 1
#                 questions()
#             elif self.currentWidget().choice2.isChecked():
#                 if self.q[self.counter][2] == -1:
#                     self.scorecard[self.q[self.counter][1]] += 1
#                     self.task_q.put(
#                         {'task_name': 'poms_baseline', 'metrics': {1: self.q[self.counter][0], 2: 1, 3: -1, 4: -1, 5: -1, 6: -1, 7: -1}})
#                 else:
#                     self.scorecard[self.q[self.counter][1]] += 3
#                     self.task_q.put(
#                         {'task_name': 'poms_baseline',
#                          'metrics': {1: self.q[self.counter][0], 2: 3, 3: -1, 4: -1, 5: -1, 6: -1, 7: -1}})
#                 self.counter += 1
#                 questions()
#             elif self.currentWidget().choice3.isChecked():
#                 if self.q[self.counter][2] == -1:
#                     self.scorecard[self.q[self.counter][1]] += 2
#                     self.task_q.put(
#                         {'task_name': 'poms_baseline', 'metrics': {1: self.q[self.counter][0], 2: 2, 3: -1, 4: -1, 5: -1, 6: -1, 7: -1}})
#                 else:
#                     self.scorecard[self.q[self.counter][1]] += 2
#                     self.task_q.put(
#                         {'task_name': 'poms_baseline',
#                          'metrics': {1: self.q[self.counter][0], 2: 2, 3: -1, 4: -1, 5: -1, 6: -1, 7: -1}})
#                 self.counter += 1
#                 questions()
#             elif self.currentWidget().choice4.isChecked():
#                 if self.q[self.counter][2] == -1:
#                     self.scorecard[self.q[self.counter][1]] += 3
#                     self.task_q.put(
#                         {'task_name': 'poms_baseline', 'metrics': {1: self.q[self.counter][0], 2: 3, 3: -1, 4: -1, 5: -1, 6: -1, 7: -1}})
#                 else:
#                     self.scorecard[self.q[self.counter][1]] += 1
#                     self.task_q.put(
#                         {'task_name': 'poms_baseline',
#                          'metrics': {1: self.q[self.counter][0], 2: 1, 3: -1, 4: -1, 5: -1, 6: -1, 7: -1}})
#                 self.counter += 1
#                 questions()
#             elif self.currentWidget().choice5.isChecked():
#                 if self.q[self.counter][2] == -1:
#                     self.scorecard[self.q[self.counter][1]] += 4
#                     self.task_q.put(
#                         {'task_name': 'poms_baseline', 'metrics': {1: self.q[self.counter][0], 2: 4, 3: -1, 4: -1, 5: -1, 6: -1, 7: -1}})
#                 else:
#                     self.scorecard[self.q[self.counter][1]] += 0
#                     self.task_q.put(
#                         {'task_name': 'poms_baseline',
#                          'metrics': {1: self.q[self.counter][0], 2: 0, 3: -1, 4: -1, 5: -1, 6: -1, 7: -1}})
#                 self.counter += 1
#                 questions()
#             else:
#                 return
#
#         def questions():
#             if self.counter < len(self.q):
#                 self.entry = self.q[self.counter]
#
#                 self.addWidget(PomsQuestionnaire(self.task_q, self.entry, 'pre'))
#
#                 self.setCurrentIndex(1)
#                 self.setCurrentWidget(self.widget(1))
#
#                 self.cleanStack()
#
#                 self.currentWidget().choice1.clicked.connect(score)
#                 self.currentWidget().choice2.clicked.connect(score)
#                 self.currentWidget().choice3.clicked.connect(score)
#                 self.currentWidget().choice4.clicked.connect(score)
#                 self.currentWidget().choice5.clicked.connect(score)
#
#             else:
#
#                 self.addWidget(PomsQuestionnaire(self.task_q, 'outro', 'pre'))
#
#                 TMD = (self.scorecard['TEN'] + self.scorecard['ANG'] + self.scorecard['CON'] + self.scorecard['FAT']
#                        + self.scorecard['DEP']) - (self.scorecard['VIG'] + self.scorecard['ERA'])
#
#                 #SCORING NEEDS TO BE OUTPUT
#
#                 self.task_q.put({'task_name': 'poms_pretest', 'metrics': {1: TMD, 2: -1, 3: -1, 4: -1, 5: -1, 6: -1, 7: -1}})
#
#                 self.setCurrentIndex(1)
#                 self.setCurrentWidget(self.widget(1))
#
#                 self.cleanStack()
#
#                 self.currentWidget().startbtn.clicked.connect(self.setCreativityEvalPre)
#
#         self.counter = 0
#         self.q = init_questionnare()
#         self.scorecard = {'TEN': 0, 'ANG': 0, 'VIG': 0, 'CON': 0, 'DEP': 0, 'ERA': 0, 'FAT': 0}
#
#         self.addWidget(PomsQuestionnaire(self.task_q, 'intro', 'pre'))
#
#         self.task_q.put({'task_name': 'poms_pretest', 'metrics': {1: 'start', 2: -1, 3: -1, 4: -1, 5: -1, 6: -1, 7: -1}})
#
#
#         self.setCurrentIndex(1)
#         self.setCurrentWidget(self.widget(1))
#
#         self.cleanStack()
#
#         self.currentWidget().startbtn.clicked.connect(questions)
#
#     def setCreativityEvalPre(self):
#         def recordEval():
#             self.task_q.put(
#                 {'task_name': 'creativity_eval', 'metrics': {1: 'RESULTS', 2: self.currentWidget().slider1.value(),
#                                                              3: self.currentWidget().slider2.value(),
#                                                              4: self.currentWidget().slider3.value(), 5: -1, 6: -1, 7: -1}})
#             self.setTransition()
#
#         self.addWidget(CreativityEvaluation(self.task_q, self.participant_id))
#
#         self.task_q.put(
#             {'task_name': 'creativity_eval', 'metrics': {1: 'start', 2: -1, 3: -1, 4: -1, 5: -1, 6: -1, 7: -1}})
#
#         self.setCurrentIndex(1)
#         self.setCurrentWidget(self.widget(1))
#
#         self.cleanStack()
#
#         self.currentWidget().startbtn.clicked.connect(recordEval)
#
#     def setTransition(self):
#         def enableButton():
#             self.currentWidget().startbtn.setEnabled(True)
#             self.currentWidget().startbtn.setCheckable(True)
#         self.addWidget(CreativityTransition())
#
#         self.task_q.put(
#             {'task_name': 'transition', 'metrics': {1: 'start', 2: -1, 3: -1, 4: -1, 5: -1, 6: -1, 7: -1}})
#
#         self.setCurrentIndex(1)
#         self.setCurrentWidget(self.widget(1))
#
#         self.currentWidget().startbtn.setEnabled(False)
#         self.currentWidget().startbtn.setCheckable(False)
#
#
#         QTimer.singleShot(3000, enableButton)
#
#         self.cleanStack()
#
#         self.currentWidget().startbtn.clicked.connect(self.setIntroFixation)
#
#     def setIntroFixation(self):
#         def enableButton():
#             self.intro.fadeout(3000)
#             self.beat_end_flag = True
#             self.setActivityOne()
#
#         def playBeat():
#             print("Playing beat")
#             self.beat.play()
#             if not self.beat_end_flag:
#                 QTimer.singleShot(self.play_rate * 1000, playBeat)
#
#         def adjustRate():
#             print("adjusting")
#             if self.play_rate < self.goal_rate:
#                 self.play_rate += self.increase_per_second
#                 QTimer.singleShot(1000, adjustRate)
#
#         # INTRO FIXATIeeON
#         self.ambiance.fadeout(2000)
#
#         if self.intro is not None:
#             if self.condition == 4:
#                 self.beat_end_flag = False
#                 self.play_rate = 1 / (120/60)
#                 self.goal_rate = 1 / (75/60)
#                 self.increase_per_second = (self.goal_rate - self.play_rate) / 15
#
#                 QTimer.singleShot(self.play_rate * 1000, playBeat)
#                 QTimer.singleShot(1000, adjustRate)
#
#             self.intro.play(fade_ms=3000)
#             length = self.intro.get_length()*1000
#             if real:
#                 QTimer.singleShot(length, enableButton)
#             else:
#                 QTimer.singleShot(1, enableButton)
#
#         else:
#             self.intro = self.ambiance
#             self.intro.play(fade_ms=3000)
#             if real:
#                 QTimer.singleShot(32000, enableButton)
#             else:
#                 QTimer.singleShot(1, enableButton)
#
#         self.addWidget(StandardFixation())
#
#         self.task_q.put({'task_name': 'intro_fixation', 'metrics': {1: -1, 2: -1, 3: -1, 4: -1, 5: -1, 6: -1, 7: -1}})
#
#         self.setCurrentIndex(1)
#         self.setCurrentWidget(self.widget(1))
#
#         self.cleanStack()
#
#     def setActivityOne(self):
#         def playBeat():
#             print("Playing beat")
#             self.beat.play()
#             if not self.beat_end_flag:
#                 QTimer.singleShot(self.play_rate * 1000, playBeat)
#
#         def adjustRate():
#             print("adjusting")
#             if self.play_rate < self.goal_rate:
#                 self.play_rate += self.increase_per_second
#                 QTimer.singleShot(1000, adjustRate)
#
#         def updateBiometrics():
#
#             print("biometrics")
#             temp = self.bio_q_algo.get()
#             if temp:
#                 self.beat_end_flag = True
#             else:
#                 self.curHR = temp['HR']
#                 self.curRR = temp['RR']
#
#                 if self.curHR > 90 or self.curHR < 70:
#                     self.play_rate = 1 / (120/60)
#                     self.increase_per_second = (self.goal_rate - self.play_rate) / 10
#                     adjustRate()
#
#                 QTimer.singleshot(250, updateBiometrics)
#
#         self.addWidget(CreativeActivityOne())
#
#         self.task_q.put(
#             {'task_name': 'activity_one', 'metrics': {1: 'start', 2: -1, 3: -1, 4: -1, 5: -1, 6: -1, 7: -1}})
#
#         # INTRO FIXATIeeON
#         self.ambiance.fadeout(2000)
#
#         if self.condition == 4:
#             self.curHR = -1
#             self.curRR = -1
#
#             self.beat_end_flag = False
#             self.play_rate = 1 / (120/60)
#             self.goal_rate = 1 / (75/60)
#             self.increase_per_second = (self.goal_rate - self.play_rate) / 15
#
#             QTimer.singleShot(self.play_rate * 1000, playBeat)
#             QTimer.singleShot(1000, adjustRate)
#             QTimer.singleShot(250, updateBiometrics)
#
#         self.body.play(loops=20)
#
#         self.setCurrentIndex(1)
#         self.setCurrentWidget(self.widget(1))
#
#         self.cleanStack()
#
#         self.currentWidget().startbtn.clicked.connect(self.setActivityTwo)
#
#     def setActivityTwo(self):
#         self.addWidget(CreativeActivityTwo())
#
#         self.task_q.put(
#             {'task_name': 'activity_two', 'metrics': {1: 'start', 2: -1, 3: -1, 4: -1, 5: -1, 6: -1, 7: -1}})
#
#         self.setCurrentIndex(1)
#         self.setCurrentWidget(self.widget(1))
#
#         self.cleanStack()
#
#         self.currentWidget().startbtn.clicked.connect(self.setOutroFixation)
#
#     def setOutroFixation(self):
#         def enableButton():
#             self.outro.fadeout(3000)
#             self.setPOMSPosttest()
#
#         self.bio_q_algo.put(True)
#         self.body.fadeout(3000)
#
#         if self.intro is not None:
#             self.intro.play(fade_ms=3000)
#             if real:
#                 QTimer.singleShot(self.outro.get_length()*1000, enableButton)
#             else:
#                 QTimer.singleShot(1, enableButton)
#
#         else:
#             self.intro = self.body
#             self.intro.play(fade_ms=3000)
#             if real:
#                 QTimer.singleShot(10000, enableButton)
#             else:
#                 QTimer.singleShot(1, enableButton)
#
#         self.addWidget(StandardFixation())
#
#         self.task_q.put({'task_name': 'outro_fixation', 'metrics': {1: 'start', 2: -1, 3: -1, 4: -1, 5: -1, 6: -1, 7: -1}})
#
#
#         self.setCurrentIndex(1)
#         self.setCurrentWidget(self.widget(1))
#
#         self.cleanStack()
#
#     def setPOMSPosttest(self):
#         def init_questionnare():
#             q = {}
#
#             q[0] = ['tense', 'TEN', -1]
#             if real:
#                 q[1] = ['angry', 'ANG', -1]
#                 q[2] = ['worn out', 'FAT', -1]
#                 q[3] = ['unhappy', 'DEP', -1]
#                 q[4] = ['proud', 'ERA', -1]
#                 q[5] = ['lively', 'VIG', -1]
#                 q[6] = ['confused', 'CON', -1]
#                 q[7] = ['sad', 'DEP', -1]
#                 q[8] = ['active', 'VIG', -1]
#                 q[9] = ['on edge', 'TEN', -1]
#                 q[10] = ['grouchy', 'ANG', -1]
#                 q[11] = ['ashamed', 'ERA', -2]
#                 q[12] = ['energetic', 'VIG', -1]
#                 q[13] = ['hopeless', 'DEP', -1]
#                 q[14] = ['uneasy', 'TEN', -1]
#                 q[15] = ['restless', 'TEN', -1]
#                 q[16] = ['cant concentrate', 'CON', -1]
#                 q[17] = ['fatigued', 'FAT', -1]
#                 q[18] = ['competent', 'ERA', -1]
#                 q[19] = ['annoyed', 'ANG', -1]
#                 q[20] = ['discourage', 'DEP', -1]
#                 q[21] = ['resentful', 'ANG', -1]
#                 q[22] = ['nervous', 'TEN', -1]
#                 q[23] = ['miserable', 'DEP', -1]
#                 q[24] = ['confident', 'ERA', -1]
#                 q[25] = ['bitter', 'ANG', -1]
#                 q[26] = ['exhausted', 'FAT', -1]
#                 q[27] = ['anxious', 'TEN', -1]
#                 q[28] = ['helpless', 'DEP', -1]
#                 q[29] = ['weary', 'FAT', -1]
#                 q[30] = ['satisified', 'ERA', -1]
#                 q[31] = ['bewildered', 'CON', -1]
#                 q[32] = ['furious', 'ANG', -1]
#                 q[33] = ['full of pep', 'VIG', -1]
#                 q[34] = ['worthless', 'DEP', -1]
#                 q[35] = ['forgetful', 'CON', -1]
#                 q[36] = ['vigorous', 'VIG', -1]
#                 q[37] = ['uncertain', 'CON', -1]
#                 q[38] = ['bushed', 'FAT', -1]
#                 q[39] = ['embarrassed', 'ERA', -2]
#
#             return q
#
#         def score():
#             if self.currentWidget().choice1.isChecked():
#                 if self.q[self.counter][2] == -1:
#                     self.scorecard[self.q[self.counter][1]] += 0
#                     self.task_q.put(
#                         {'task_name': 'poms_baseline', 'metrics': {1: self.q[self.counter][0], 2: 0, 3: -1, 4: -1, 5: -1, 6: -1, 7: -1}})
#                 else:
#                     self.scorecard[self.q[self.counter][1]] += 4
#                     self.task_q.put(
#                         {'task_name': 'poms_baseline',
#                          'metrics': {1: self.q[self.counter][0], 2: 4, 3: -1, 4: -1, 5: -1, 6: -1, 7: -1}})
#                 self.counter += 1
#                 questions()
#             elif self.currentWidget().choice2.isChecked():
#                 if self.q[self.counter][2] == -1:
#                     self.scorecard[self.q[self.counter][1]] += 1
#                     self.task_q.put(
#                         {'task_name': 'poms_baseline', 'metrics': {1: self.q[self.counter][0], 2: 1, 3: -1, 4: -1, 5: -1, 6: -1, 7: -1}})
#                 else:
#                     self.scorecard[self.q[self.counter][1]] += 3
#                     self.task_q.put(
#                         {'task_name': 'poms_baseline',
#                          'metrics': {1: self.q[self.counter][0], 2: 3, 3: -1, 4: -1, 5: -1, 6: -1, 7: -1}})
#                 self.counter += 1
#                 questions()
#             elif self.currentWidget().choice3.isChecked():
#                 if self.q[self.counter][2] == -1:
#                     self.scorecard[self.q[self.counter][1]] += 2
#                     self.task_q.put(
#                         {'task_name': 'poms_baseline', 'metrics': {1: self.q[self.counter][0], 2: 2, 3: -1, 4: -1, 5: -1, 6: -1, 7: -1}})
#                 else:
#                     self.scorecard[self.q[self.counter][1]] += 2
#                     self.task_q.put(
#                         {'task_name': 'poms_baseline',
#                          'metrics': {1: self.q[self.counter][0], 2: 2, 3: -1, 4: -1, 5: -1, 6: -1, 7: -1}})
#                 self.counter += 1
#                 questions()
#             elif self.currentWidget().choice4.isChecked():
#                 if self.q[self.counter][2] == -1:
#                     self.scorecard[self.q[self.counter][1]] += 3
#                     self.task_q.put(
#                         {'task_name': 'poms_baseline', 'metrics': {1: self.q[self.counter][0], 2: 3, 3: -1, 4: -1, 5: -1, 6: -1, 7: -1}})
#                 else:
#                     self.scorecard[self.q[self.counter][1]] += 1
#                     self.task_q.put(
#                         {'task_name': 'poms_baseline',
#                          'metrics': {1: self.q[self.counter][0], 2: 1, 3: -1, 4: -1, 5: -1, 6: -1, 7: -1}})
#                 self.counter += 1
#                 questions()
#             elif self.currentWidget().choice5.isChecked():
#                 if self.q[self.counter][2] == -1:
#                     self.scorecard[self.q[self.counter][1]] += 4
#                     self.task_q.put(
#                         {'task_name': 'poms_baseline', 'metrics': {1: self.q[self.counter][0], 2: 4, 3: -1, 4: -1, 5: -1, 6: -1, 7: -1}})
#                 else:
#                     self.scorecard[self.q[self.counter][1]] += 0
#                     self.task_q.put(
#                         {'task_name': 'poms_baseline',
#                          'metrics': {1: self.q[self.counter][0], 2: 0, 3: -1, 4: -1, 5: -1, 6: -1, 7: -1}})
#                 self.counter += 1
#                 questions()
#             else:
#                 return
#
#         def questions():
#             if self.counter < len(self.q):
#                 self.entry = self.q[self.counter]
#
#                 self.addWidget(PomsQuestionnaire(self.task_q, self.entry, 'post'))
#
#                 self.setCurrentIndex(1)
#                 self.setCurrentWidget(self.widget(1))
#
#                 self.cleanStack()
#
#                 self.currentWidget().choice1.clicked.connect(score)
#                 self.currentWidget().choice2.clicked.connect(score)
#                 self.currentWidget().choice3.clicked.connect(score)
#                 self.currentWidget().choice4.clicked.connect(score)
#                 self.currentWidget().choice5.clicked.connect(score)
#
#             else:
#
#                 self.addWidget(PomsQuestionnaire(self.task_q, 'outro', 'post'))
#
#                 TMD = (self.scorecard['TEN'] + self.scorecard['ANG'] + self.scorecard['CON'] + self.scorecard['FAT']
#                        + self.scorecard['DEP']) - (self.scorecard['VIG'] + self.scorecard['ERA'])
#
#                 #SCORING NEEDS TO BE OUTPUT
#
#                 self.task_q.put({'task_name': 'poms_posttest', 'metrics': {1: TMD, 2: -1, 3: -1, 4: -1, 5: -1, 6: -1, 7: -1}})
#
#                 self.setCurrentIndex(1)
#                 self.setCurrentWidget(self.widget(1))
#
#                 self.cleanStack()
#
#                 self.currentWidget().startbtn.clicked.connect(self.setCreativityEvalPost)
#
#         self.counter = 0
#         self.q = init_questionnare()
#         self.scorecard = {'TEN': 0, 'ANG': 0, 'VIG': 0, 'CON': 0, 'DEP': 0, 'ERA': 0, 'FAT': 0}
#
#         self.addWidget(PomsQuestionnaire(self.task_q, 'intro', 'post'))
#
#         self.task_q.put({'task_name': 'poms_posttest', 'metrics': {1: 'start', 2: -1, 3: -1, 4: -1, 5: -1, 6: -1, 7: -1}})
#
#         self.body.fadeout(3000)
#
#         self.outro.play()
#
#         self.setCurrentIndex(1)
#         self.setCurrentWidget(self.widget(1))
#
#         self.cleanStack()
#
#         self.currentWidget().startbtn.clicked.connect(questions)
#
#     def setCreativityEvalPost(self):
#         def recordEval():
#             self.task_q.put(
#                 {'task_name': 'creativity_eval', 'metrics': {1: 'RESULTS', 2: self.currentWidget().slider1.value(),
#                                                              3: self.currentWidget().slider2.value(),
#                                                              4: self.currentWidget().slider3.value(), 5: -1, 6: -1, 7: -1}})
#             self.setEnd()
#
#         self.addWidget(CreativityEvaluation(self.task_q, self.participant_id))
#
#         self.task_q.put(
#             {'task_name': 'creativity_eval', 'metrics': {1: 'start', 2: -1, 3: -1, 4: -1, 5: -1, 6: -1, 7: -1}})
#
#         self.setCurrentIndex(1)
#         self.setCurrentWidget(self.widget(1))
#
#         self.cleanStack()
#
#         self.currentWidget().startbtn.clicked.connect(recordEval)
#
#     def setEnd(self):
#         self.addWidget(End())
#
#         self.task_q.put({'task_name': 'end', 'metrics': {1: 'end', 2: -1, 3: -1, 4: -1, 5: -1, 6: -1, 7: -1}})
#
#         self.setCurrentIndex(1)
#         self.setCurrentWidget(self.widget(1))
#
#         self.cleanStack()
