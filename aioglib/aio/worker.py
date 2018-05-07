from gi.repository import GLib
try:
	# We need a real thread, even if gevent has monkeypatched threads.
	from gevent.threadpool import ThreadPoolExecutor
except ImportError:
	from concurrent.futures import ThreadPoolExecutor


def worker():
	GLib.MainLoop().run()


def launch():
	executor = ThreadPoolExecutor(max_workers=1)
	executor.submit(worker)
