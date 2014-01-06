#Defined classes used to handle logs on the server

runLevel = 1
NORMAL = 1
DEBUG = 2

def init(level):
    global runLevel
    runLevel = level

class threadLog:
    def __init__(self):
        pass
    
    def __del__(self):
        pass
    
    def log(self, text):
        if runLevel < NORMAL:
            return
        else:
            pass
    
    def debug(self, text):
        if runLevel < DEBUG:
            return
        else:
            pass
    
    pass
