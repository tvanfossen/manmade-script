from queue import Queue
from utils.Games import DrivingGame, PongGame, WisconsinCardSort
from utils.DataCollection import DataLogger
from multiprocessing import Process

if __name__ == '__main__':
    # d = DrivingGame(Queue(), Queue(), 1, 'trial')
    p = PongGame(Queue(), Queue(), 1, 'trial')
    # wcst = WisconsinCardSort(Queue(), Queue(), 4, 60, 'experiment', 'trial')

