import sys
from .worker import launch as launch_worker


try:
	from . import block_native
except ImportError as e:
	print(e)

try:
	from . import block_worker
except ImportError as e:
	print(e)

try:
	from . import gevent_worker
except ImportError as e:
	print(e)


def _is_gevent_monkey_patched():
	if 'gevent.monkey' not in sys.modules:
		return False
	import gevent.socket
	import socket
	return socket.socket is gevent.socket.socket


override_sync_await = None

def sync_await(coro):
	if override_sync_await:
		return override_sync_await(coro)

	if _is_gevent_monkey_patched():
		return gevent_worker.sync_await(coro)

	return block_native.sync_await(coro)
