import threading
from message import *
class agentUDP(threading.Thread):
    def __init__(self, conn, buffer, buffer_lock):
        threading.Thread.__init__(self)

        self.conn = conn
        self.buffer = buffer
        self.buffer_lock = buffer_lock
        self.go = True
        self.msg = Message()


    def stopAgent(self):
        self.go = False


    def run(self):
        retry = 0
        self.msg.makeMessage("", Message.TYPE_KAL, 0)
        m = self.msg.classToBinary()
        self.conn.set_timeout(0.6)

        while self.go:
            
            while retry < 3:
                try:
                    msg = self.conn.receive_lite()
                    
                    with self.buffer_lock:
                        self.buffer.append(msg)
                        self.buffer_lock.notify()

                    retry = 0

                except Exception:
                    retry += 1

            self.conn.keepAlive(m)

        print("agent has stoped")

        
