import asyncio


Event = asyncio.Event
sleep = asyncio.sleep


class AioToken:
	def __init__(self, loop):
		self.loop = loop

	def run_sync_soon(self, sync_fn, *args):
		self.loop.call_soon_threadsafe(sync_fn, *args)


def current_aio_token():
	loop = asyncio.get_event_loop()
	if not loop.is_running():
		raise RuntimeError('No active event loop.')
	return AioToken(loop)


class Future:
	def __init__(self):
		self.event = Event()

	def set(self, outcome):
		self.outcome = outcome
		self.event.set()

	async def wait(self):
		await self.event.wait()
		return self.outcome.unwrap()

	def __await__(self):
		return self.wait().__await__()


class UnboundedQueue(asyncio.Queue):
	def __aiter__(self):
		return self

	async def __anext__(self):
		return [await self.get()]


class TaskStatus(asyncio.Future):
	def started(self, value=None):
		self.set_result(value)


class Nursery:
	def start(self, async_fn, *args):
		ts = TaskStatus()
		self.children.append(self.loop.create_task(async_fn(*args, task_status=ts)))
		return ts

	def start_soon(self, async_fn, *args):
		self.children.append(self.loop.create_task(async_fn(*args)))

	async def __aenter__(self):
		self.loop = asyncio.get_event_loop()
		self.children = []
		return self

	async def __aexit__(self, exc_type, exc, tb):
		for child in self.children:
			await child


def open_nursery():
	return Nursery()
