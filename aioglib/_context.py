from contextlib import contextmanager
from gi.repository import GLib


@contextmanager
def push_main_context(ctx):
	GLib.MainContext.push_thread_default(ctx)
	try:
		yield
	finally:
		GLib.MainContext.pop_thread_default(ctx)


def get_main_context():
    return GLib.MainContext.get_thread_default() or GLib.MainContext.default()
