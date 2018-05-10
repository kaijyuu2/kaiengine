# -*- coding: utf-8 -*-

import os
import asyncio
import sys

from asyncio.streams import StreamWriter, FlowControlMixin

reader, writer = None, None

@asyncio.coroutine
def _stdio(loop=None):
    if loop is None:
        loop = asyncio.get_event_loop()

    reader = asyncio.StreamReader()
    reader_protocol = asyncio.StreamReaderProtocol(reader)

    writer_transport, writer_protocol = yield from loop.connect_write_pipe(FlowControlMixin, sys.stdout)
    writer = StreamWriter(writer_transport, writer_protocol, None, loop)

    yield from loop.connect_read_pipe(lambda: reader_protocol, sys.stdin)

    return reader, writer

@asyncio.coroutine
def asyncInput(message):
    if isinstance(message, str):
        message = message.encode('utf8')

    global reader, writer
    if (reader, writer) == (None, None):
        reader, writer = yield from _stdio()

    writer.write(message)
    yield from writer.drain()

    line = yield from reader.readline()
    return line.decode('utf8').replace('\r', '').replace('\n', '')
