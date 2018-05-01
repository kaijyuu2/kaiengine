# -*- coding: utf-8 -*-

import asyncio

def runCoroutine(coroutine, callback = None):
    future = asyncio.Future()
    asyncio.ensure_future(coroutine(future))
    if callback is not None:
        future.add_done_callback(callback)