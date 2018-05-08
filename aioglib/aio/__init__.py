from .._py37.contextlib import asynccontextmanager
from functools import partial
from gi.repository import Gio
from outcome import capture

from .._context import get_main_context
from .worker import launch as launch_worker


__all__ = ['sleep', 'open_nursery', 'launch_worker', 'run', 'watch']

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


def get_engine():
	for engine in engines:
		try:
			engine.current_aio_token()
		except RuntimeError:
			pass
		else:
			return engine
	raise RuntimeError('No active event loop.')


def sleep(seconds):
	aio = get_engine()

	return aio.sleep(seconds)


def open_nursery():
	aio = get_engine()

	return aio.open_nursery()


def _wrap_callable(fn, wake_up):
	return lambda _, *args: wake_up(capture(fn, *args))


async def run(start, finish, *args):
	aio = get_engine()

	finished = aio.Future()
	finished_set = partial(aio.current_aio_token().run_sync_soon, finished.set)

	cancellable = Gio.Cancellable.new()
	def start_fn():
		start(*([arg for arg in args] + [cancellable, _wrap_callable(finish, finished_set)]))
	get_main_context().invoke_full(0, start_fn)

	try:
		return await finished
	except BaseException:
		cancellable.cancel()
		raise


@asynccontextmanager
async def watch(install, uninstall, *args):
	aio = get_engine()

	installed = aio.Future()
	installed_set = partial(aio.current_aio_token().run_sync_soon, installed.set)

	queue = aio.UnboundedQueue() # TODO apply backpressure
	queue_put = partial(aio.current_aio_token().run_sync_soon, queue.put_nowait)

	def install_fn():
		installed_set(capture(install, *[_wrap_callable(arg, queue_put) if callable(arg) else arg for arg in args]))
	get_main_context().invoke_full(0, install_fn)

	installation_id = await installed # TODO disable cancellation during this await

	try:
		async def generator():
			async for batch in queue:
				for outcome in batch:
					yield outcome.unwrap()
		yield generator()
	finally:
		get_main_context().invoke_full(0, lambda: uninstall(installation_id)) # TODO wait until uninstallation finished
