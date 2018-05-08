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
from aioglib.aio import sleep, open_nursery
from gi.repository import Gio


xml = """
<node>
	<interface name='net.lew21.aioglib.Test'>
		<method name='HelloWorld'>
			<arg type='s' name='response' direction='out'/>
		</method>
		<method name='Quit'/>
	</interface>
</node>
"""


async def serve(listener):
	async for call in listener:
		assert call.interface_name == 'net.lew21.aioglib.Test'
		if call.method_name == 'HelloWorld':
			call.invocation.return_value(Variant('(s)', ("Hello world!",)))
		elif call.method_name == 'Quit':
			call.invocation.return_value(None)
			await sleep(1)
			return
		else:
			print(call)


async def main():
	bus = await bus_get(BusType.SESSION)

	async with open_nursery() as nursery:
		iface = Gio.DBusNodeInfo.new_for_xml(xml).interfaces[0]
		async with bus.register_object('/', iface) as listener:
			nursery.start_soon(serve, listener)

			assert (await bus.call(
				'org.freedesktop.DBus',
				'/org/freedesktop/DBus',
				'org.freedesktop.DBus',
				'RequestName',
				Variant('(su)', ('net.lew21.aioglib.Test', 4)),
				VariantType('(u)'),
				0,
				MAXINT
			)).unpack() == (1,)

			assert (await bus.call(
				'net.lew21.aioglib.Test',
				'/',
				'net.lew21.aioglib.Test',
				'HelloWorld',
				Variant('()', ()),
				VariantType('(s)'),
				0,
				MAXINT
			)).unpack() == ('Hello world!',)

			assert (await bus.call(
				'net.lew21.aioglib.Test',
				'/',
				'net.lew21.aioglib.Test',
				'Quit',
				Variant('()', ()),
				VariantType('()'),
				0,
				MAXINT
			)).unpack() == ()


sync_await(main)
