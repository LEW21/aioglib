from gbulb import GLibEventLoop

from ..util import push_main_context, push_event_loop


def sync_await(coro):
	print('block+native')
	loop = GLibEventLoop()
	with push_main_context(loop._context):
		with push_event_loop(loop):
			return loop.run_until_complete(coro())
