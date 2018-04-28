# -*- coding: utf-8 -*-

#the object for the main scheduler


import asyncio

scheduler = None

def stopGameScheduler():
    if scheduler:
        scheduler.stop()
        

def initializeGame(init, close):
    global scheduler
    
    scheduler = asyncio.get_event_loop()
    
    init()
    
    from kaiengine.event import addGameCloseListener
    addGameCloseListener(stopGameScheduler, 99999999999999999999999999999999999999999999999)
    
    try:
        scheduler.run_forever()
    except:
        import traceback
        traceback.print_stack()
    finally:
        try:
            close()
        except:
            pass
        
        
def getGameScheduler():
    return scheduler