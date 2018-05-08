from asyncio import Future, get_event_loop, run_coroutine_threadsafe
from functools import partial

from . import worker
from .util import set_future_from


def sync_await(coro):
	print('block+sync.worker')
	res = Future()
	set_res_from = partial(get_event_loop().call_soon_threadsafe, set_future_from, res)
	run_coroutine_threadsafe(coro(), loop=worker.loop).add_done_callback(lambda fut: set_res_from(lambda: fut.result()))
	return get_event_loop().run_until_complete(res)
