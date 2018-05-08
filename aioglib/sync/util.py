from asyncio import get_event_loop, set_event_loop
from contextlib import contextmanager


@contextmanager
def push_event_loop(loop):
	try:
		old_loop = get_event_loop()
	except RuntimeError:
		old_loop = None
	set_event_loop(loop)
	try:
		yield
	finally:
		set_event_loop(old_loop)


def set_future_from(future, fn):
	try:
		res = fn()
	except Exception as e:
		future.set_exception(e)
	else:
		future.set_result(res)
