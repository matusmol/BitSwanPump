import logging

import bspump
import time
import bspump.common
import bspump.random
import bspump.trigger
from lookup import MyIndexLookup


##

L = logging.getLogger(__name__)

##


class SlaveApplication(bspump.BSPumpApplication):
	def __init__(self):
		super().__init__()

		svc = self.get_service("bspump.PumpService")
		
		self.Lookup = MyIndexLookup(self, id='MyLookup', config={'master_url':'http://localhost:8080', 'master_lookup_id':"MyLookup"})

		svc.add_lookup(self.Lookup)
		svc.add_pipeline(SlavePipeline(self))
		

class SlavePipeline(bspump.Pipeline):
	def __init__(self, app, pipeline_id=None):
		super().__init__(app, pipeline_id)
		lb = 1567353600 - 60*60*5
		ub = 1567548000 + 60*60*5
		channel_choice = list(range(12, 1190))
		self.build(
			bspump.random.RandomSource(app, self,
				config={'number': 10, 'upper_bound': 10}
			).on(bspump.trigger.OpportunisticTrigger(app, chilldown_period=1)),
			bspump.random.RandomEnricher(app, self, config={'field':'@timestamp', 'lower_bound':lb, 'upper_bound': ub}, id="RE0"),
			bspump.random.RandomEnricher(app, self, choice=channel_choice, config={'field':'channel'}, id="RE1"),
			Enricher(app, self), 
			bspump.common.PPrintSink(app, self)
		)


class Enricher(bspump.Processor):

	def __init__(self, app, pipeline, id=None, config=None):
		super().__init__(app, pipeline, id, config)
		svc = app.get_service("bspump.PumpService")
		self.Lookup = svc.locate_lookup("MyLookup")

	
	def process(self, context, event):
		# enrich with TV-program and it's name
		timestamp = event['@timestamp']
		channel = event['channel']
		st = time.time()
		condition = (self.Lookup.Matrix.Array['channelid'] == channel) & (self.Lookup.Matrix.Array['ts_start'] <= timestamp) & (self.Lookup.Matrix.Array['ts_end'] > timestamp) 
		
		
		
		program_id = self.Lookup.search(condition)
		if program_id is None:
			print('noup :(')
			return event
		
		event['program_id'] = program_id
		end = time.time()

		L.warn("{}".format(end-st))
		return event


if __name__ == '__main__':
	app = SlaveApplication()
	app.run()
