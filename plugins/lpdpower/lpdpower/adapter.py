from odin.adapters.adapter import ApiAdapter, ApiAdapterResponse, request_types, response_types
from tornado.escape import json_decode
from concurrent import futures
from tornado.ioloop import IOLoop
from tornado.concurrent import run_on_executor
from pscu_data import PSCUData
import time
import sys


class NullDevice():
    def write(self, s):
        pass


class LPDPowerAdapter(ApiAdapter):

	# Thread executor used for background tasks
	executor = futures.ThreadPoolExecutor(max_workers=1)
	
	def __init__(self, **kwargs):
		super(LPDPowerAdapter, self).__init__(**kwargs)

		sys.stdout = NullDevice() #Prevent I2C spam if devices aren't connected

		self.pscuData = PSCUData()

		self.update_interval = self.options.get('update_interval', 0.05)
		self.update_loop()

	@request_types('application/json')
	@response_types('application/json')
	def get(self, path, request):
		return ApiAdapterResponse(self.pscuData.dataTree.getData(path))	

	@request_types('application/json')
        @response_types('application/json')
        def put(self, path, request):
		data = json_decode(request.body)
		self.pscuData.dataTree.setData(path, data)
		return ApiAdapterResponse(self.pscuData.dataTree.getData(path))  

	#@run_on_executor
	def update_loop(self):	
		self.pscuData.pscu.updateLCD()
		self.pscuData.pscu.pollAllSensors()
		time.sleep(self.update_interval)
		IOLoop.instance().add_callback(self.update_loop)
