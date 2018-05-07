from gi.repository import GLib
try:
	# We need a real thread, even if gevent has monkeypatched threads.
	from gevent.threadpool import ThreadPoolExecutor
except ImportError:
	from concurrent.futures import ThreadPoolExecutor

from gbulb import GLibEventLoop
from ..util import push_main_context, push_event_loop, get_main_context


loop = None


def worker():
	with push_main_context(loop._context):
		with push_event_loop(loop):
			loop.run_forever()


def launch():
	global loop
	loop = GLibEventLoop(context=GLib.MainContext.default())
	executor = ThreadPoolExecutor(max_workers=1)
	executor.submit(worker)
