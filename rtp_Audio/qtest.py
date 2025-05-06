import queue
import time
import threading

q = queue.Queue()
def send_msgs(q,ev):
    for i in range(0,100,10):
        q.put(f"Worker {i} arrived.")
        time.sleep(1)

    ev.set()


def recv_msgs(q,ev):
    while not ev.is_set():
        print(q.get())

ev = threading.Event()
th1 = threading.Thread(target=send_msgs,args=(q,ev))
th2 = threading.Thread(target=recv_msgs,args=(q,ev))

th1.start()
th2.start()