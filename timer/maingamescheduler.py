# -*- coding: utf-8 -*-

#the object for the main scheduler

import asyncio

from math import inf

scheduler = None

def stopGameScheduler():
    if scheduler:
        scheduler.stop()
        

def initializeGame(init, close):
    global scheduler
    
    scheduler = asyncio.get_event_loop()
    
    init()
    
    from kaiengine.event import addGameCloseListener
    addGameCloseListener(stopGameScheduler, inf)
    
    try:
        scheduler.run_forever()
    except:
        import traceback
        traceback.print_exc()
    finally:
        try:
            close()
        except:
            pass
        
        
def getGameScheduler():
    return scheduler