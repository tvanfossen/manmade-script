import csv
from PyQt5.QtCore import QTime
import serial
from queue import Queue
import pygame

real = True

class BiometricTracking:
    def __init__(self, q, q_algo):
        self.q = q
        self.q_algo = q_algo

        if real:
            ser = serial.Serial()
            ser.port = '/dev/ttyUSB0'
            ser.baudrate = 115200
            ser.timeout = 0

            ser.open()
            final = []

            curHR = -1
            curRR = -1

            while 1:
                pygame.time.delay(50)

                temp = ser.readline()

                if len(temp) > 1:
                    temp = temp.decode('utf-8')
                    temp = temp.split('\r\n')


                    for i in temp:
                        temp2 = i.split(',')
                        if 'fHR' in temp2:
                            final.append(temp2)
                        elif 'fRR' in temp2:
                            final.append(temp2)

                    if len(final) == 2:
                        for i in final:
                            if i[0] == 'fRR':
                                curRR = i[1]
                            elif i[0] == 'fHR':
                                curHR = i[1]

                        final = []

                        self.q.put({'HR': curHR, 'RR': curRR})
                        self.q_algo.put({'HR': curHR, 'RR': curRR})
        else:
            while 1:
                pygame.time.delay(50)
                self.q.put({'HR': -1, 'RR': -1})
                self.q_algo.put({'HR': 80, 'RR': 20})


class DataLogger:
    def __init__(self, bio_q, task_q, participant_id, condition):
        print("data logger init")

        cond_string = ""
        if condition == 1:
            cond_string = "STA"
        elif condition == 2:
            cond_string = "STK"
        elif condition == 3:
            cond_string = "OA"
        elif condition == 4:
            cond_string = "DYN"

        self.filename = "output/participant"+str(participant_id)+cond_string+"_output.csv"
        self.init_file(self.filename)
        self.main_logger(bio_q, task_q, participant_id, condition)

        # Not efficient, but works for now. Just experimental anyways

    def main_logger(self, bio_q, task_q, participant_id, condition):

        self.curHR = -1
        self.curRR = -1

        self.cur_task = 'None'
        self.task_temp = None
        self.last_task = None
        self.metrics = [-1, -1, -1, -1, -1, -1, -1]

        # Could change implementation to QThread + QTimer if issues
        pygame.init()
        pygame.time.set_timer(pygame.USEREVENT+7, 100)



        while 1:
            pygame.time.delay(90)

            # pygame.init() shared across threads, init before and after timer to ensure no breaks

            pygame.init()
            for event in pygame.event.get():
                if event.type == pygame.USEREVENT + 7:
                    with open(self.filename, 'a') as output:
                        self.output_writer = csv.writer(output, delimiter=',')
                        self.output_writer.writerow(
                            [self.cur_timestamp(), self.curHR, self.curRR, participant_id, condition, self.cur_task,
                             self.metrics[0], self.metrics[1], self.metrics[2], self.metrics[3], self.metrics[4],
                             self.metrics[5], self.metrics[6]])

            if bio_q.qsize() > 0:
                bio_temp = bio_q.get_nowait()
                if bio_temp is not None:
                    self.curHR = bio_temp['HR']
                    self.curRR = bio_temp['RR']
            if task_q.qsize() > 0:
                self.task_temp = task_q.get_nowait()
                if self.task_temp is not None:
                    print(self.task_temp)
                    self.cur_task = self.task_temp['task_name']

                    for i in self.task_temp['metrics']:
                        self.metrics[i-1] = self.task_temp['metrics'][i]

    def cur_timestamp(self):
        time = QTime.currentTime()
        return str(time.hour()) + ":" + str(time.minute()) + ":" + str(time.second()) + "." + str(time.msec())

    def init_file(self, filename):
        with open(filename, 'w') as output:
            output_writer = csv.writer(output, delimiter=',')
            output_writer.writerow(["Time", "HR", "RR", "participant_id", "condition", "Task Name", "Metric 1", "Metric 2", "Metric 3", "Metric 4",
                                    "Metric 5", "Metric 6", "Metric 7"])
