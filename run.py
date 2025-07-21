
# To run Jarvis
import multiprocessing
import subprocess

def startJarvis(queue):
    print("Process 1 is running.")
    from main import start
    start(queue)

def listenHotword(queue):
    print("Process 2 is running.")
    from Backend.features import hotword
    hotword(queue)

if __name__ == '__main__':
    queue = multiprocessing.Queue()
    p1 = multiprocessing.Process(target=startJarvis, args=(queue,))
    p2 = multiprocessing.Process(target=listenHotword, args=(queue,))
    p1.start()
    p2.start()
    p1.join()

    if p2.is_alive():
        p2.terminate()
        p2.join()

    print("system stop")