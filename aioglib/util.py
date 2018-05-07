from contextlib import contextmanager
from asyncio import get_event_loop, set_event_loop
from gi.repository import GLib


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


@contextmanager
def push_main_context(ctx):
	GLib.MainContext.push_thread_default(ctx)
	try:
		yield
	finally:
		GLib.MainContext.pop_thread_default(ctx)


def get_main_context():
    return GLib.MainContext.get_thread_default() or GLib.MainContext.default()


def set_future_from(future, fn):
	try:
		res = fn()
	except Exception as e:
		future.set_exception(e)
	else:
		future.set_result(res)
