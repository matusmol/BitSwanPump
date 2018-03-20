import logging
import asyncio
from .. import Source

#

L = logging.getLogger(__file__)

#

class FileLineSource(Source):


	ConfigDefaults = {
		'path': '',
		'mode': 'rb',
	}


	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)
		self.Loop = app.Loop
		self._future = None


	async def _read_file(self):
		filename = self.Config['path']
		mode = self.Config['mode']

		await self.Pipeline.ready()

		try:
			if filename.endswith(".gz"):
				import gzip
				f = gzip.open(filename, 'rb')

			elif filename.endswith(".bz2"):
				import bz2
				f = bz2.open(filename, 'rb')

			elif filename.endswith(".xz") or filename.endswith(".lzma"):
				import lzma
				f = lzma.open(filename, 'rb')
			else:
				f = open(filename, 'rb')

		except IOError:
			L.error("The specified file {} could not be opened.".format(self.Config['path']))
		
		for line in f:
			await self.Pipeline.ready()
			self.process(line)

		f.close()

	async def start(self):
		self._future = asyncio.ensure_future(self._read_file(), loop=self.Loop)


class FileBlockSource(Source):


	ConfigDefaults = {
		'path': '',
		'mode': 'rb',
	}


	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)
		self.Loop = app.Loop
		self._future = None


	async def _read_file(self):
		
		filename = self.Config['path']
		mode = self.Config['mode']

		await self.Pipeline.ready()

		with open(filename, mode) as f:
			event = f.read()

		self.process(event)



	async def start(self):
		self._future = asyncio.ensure_future(self._read_file(), loop=self.Loop)
