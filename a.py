import threading
import Queue

active_queues = []

class Worker(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.mailbox = Queue.Queue()
        active_queues.append(self.mailbox)

    def run(self):
        while True:
            data = self.mailbox.get()
            if data == 'shutdown':
                print self, 'shutting down'
                return
            print self, 'received a message:', data

    def stop(self):
        active_queues.remove(self.mailbox)
        self.mailbox.put("shutdown")
        self.join()


def broadcast_event(data):
    for q in active_queues:
        q.put(data)

t1 = Worker()
t2 = Worker()
t1.start()
t2.start()