import sys
from enum import Enum

class Mode(Enum):
	aio_native = 1
	aio_asyncio = 2
	aio_trio = 3
	sync_block_native = 4
	sync_block_worker = 5
	sync_gevent_worker = 6
	sync_gevent_nomonkey_worker = 7

mode = Mode(int(sys.argv[1]) if len(sys.argv) > 1 else 1)
print(mode)

if mode == Mode.aio_native:
	# No worker necessary
	import gbulb
	gbulb.install()
	import asyncio
	def sync_await(coro):
		return asyncio.get_event_loop().run_until_complete(coro())

elif mode == Mode.aio_asyncio:
	from aioglib import aio
	aio.launch_worker()
	import asyncio
	def sync_await(coro):
		return asyncio.get_event_loop().run_until_complete(coro())

elif mode == Mode.aio_trio:
	from aioglib import aio
	aio.launch_worker()
	import trio
	def sync_await(coro):
		return trio.run(coro)

elif mode == Mode.sync_block_native:
	# No worker necessary
	from aioglib.sync import sync_await

elif mode == Mode.sync_block_worker:
	from aioglib import sync
	from aioglib.sync import sync_await
	sync.launch_worker()
	sync.override_sync_await = sync.block_worker.sync_await

elif mode == Mode.sync_gevent_worker:
	from gevent import monkey
	monkey.patch_all()
	from aioglib import sync
	from aioglib.sync import sync_await
	sync.launch_worker()

elif mode == Mode.sync_gevent_nomonkey_worker:
	from aioglib import sync
	from aioglib.sync import sync_await
	sync.launch_worker()
	sync.override_sync_await = sync.gevent_worker.sync_await


from aioglib.dbus import bus_get, BusType, MAXINT, Variant, VariantType

async def main():
	bus = await bus_get(BusType.SESSION)
	assert((await bus.call(
		'org.freedesktop.Notifications',
		'/org/freedesktop/Notifications',
		'org.freedesktop.Notifications',
		'Notify',
		Variant('(susssasa{sv}i)', ('aioglib', 123, 'aioglib', 'Something happened', 'Lorem ipsum dolor sit amet', [], {}, 2000)),
		VariantType('(u)'),
		0,
		MAXINT
	)).unpack() == (123,))


async def dummy():
	return 5

assert(sync_await(dummy) == 5)

sync_await(main)
