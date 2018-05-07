from gi.repository import Gio
from functools import partial

import asyncio

from ..util import get_main_context, set_future_from


def is_active():
	try:
		return asyncio.get_event_loop().is_running()
	except RuntimeError:
		return False


class GLibTask(asyncio.Future):
	def __init__(self, op):
		super().__init__()
		self._gio_cancellable = Gio.Cancellable.new()
		op(self)

	def cancel(self):
		if self.done():
			return False
		self._gio_cancellable.cancel()
		return True


def call(start, finish, *args):
	def op(res):
		cancellable = res._gio_cancellable
		set_res_from = partial(asyncio.get_event_loop().call_soon_threadsafe, set_future_from, res)
		def start_fn():
			start(*([arg for arg in args] + [cancellable, (lambda _, cbres: set_res_from(lambda: finish(cbres)))]))
		get_main_context().invoke_full(0, start_fn)

	return GLibTask(op)
