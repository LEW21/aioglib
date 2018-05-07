from .worker import launch as launch_worker

__all__ = ['launch_worker', 'call']

engines = []

try:
	from . import asyncio
except ImportError as e:
	print(e)
else:
	engines.append(asyncio)

try:
	from . import trio
except ImportError as e:
	print(e)
else:
	engines.append(trio)


def call(start, finish, *args):
	for engine in engines:
		if engine.is_active():
			return engine.call(start, finish, *args)
	raise RuntimeError('No active event loop.')
