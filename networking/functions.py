# -*- coding: utf-8 -*-

import asyncio

def runCoroutine(coroutine, callback):
    future = asyncio.Future()
    asyncio.ensure_future(coroutine(future))
    future.add_done_callback(callback)