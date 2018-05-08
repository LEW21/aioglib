try:
	import trio.hazmat
except NotImplementedError as e:
	raise ImportError('Cannot import trio', e)


current_aio_token = trio.hazmat.current_trio_token
Event = trio.Event
UnboundedQueue = trio.hazmat.UnboundedQueue
sleep = trio.sleep
open_nursery = trio.open_nursery


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
