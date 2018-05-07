from asyncio import run_coroutine_threadsafe
from functools import partial
from gevent.event import AsyncResult
from gevent.threadpool import ThreadResult

from ..util import set_future_from
from . import worker


class GFuture(AsyncResult):
	def set_result(self, val):
		self.set(val)


class GSafeFuture(ThreadResult):
	def set_result(self, val):
		self.set(val)

	def set_exception(self, e):
		self.handle_error(None, e)


def sync_await(coro):
	print('gevent+sync.worker')
	res = GFuture()
	set_res_from = partial(set_future_from, GSafeFuture(res))
	run_coroutine_threadsafe(coro(), loop=worker.loop).add_done_callback(lambda fut: set_res_from(lambda: fut.result()))
	return res.wait()
