from bspump import Processor
import collections


class LatchProcessor(Processor):

	ConfigDefaults = {
		'queue_max_size': 50,  # 0 means unlimited size
	}

	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, id=id, config=config)
		max_size = int(self.Config.get('queue_max_size'))
		if max_size == 0:
			self.Queue = collections.deque()
		else:
			self.Queue = collections.deque(maxlen=max_size)

	def process(self, context, event):
		self.Queue.append(event)
		return event
