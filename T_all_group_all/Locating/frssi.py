from subprocess import Popen, PIPE # Used to run native OS commads in python wrapped subproccess
import numpy # Used for matrix operations in localization algorithm

class RSSIScanner():
	# Allows us to declare a network interface externally.
	def __init__(self, interface):
		self.interface = interface

	def getRawNetworkScan(self, sudo=False):
		# Scan command 'iwlist interface scan' needs to be fed as an array.
		if sudo:
			scan_command = ['sudo','iwlist',self.interface,'scan']
		else:
			scan_command = ['iwlist',self.interface,'scan']
		# Open a subprocess running the scan command.
		scan_process = Popen(scan_command, stdout=PIPE, stderr=PIPE)
		# Returns the 'success' and 'error' output.
		(raw_output, raw_error) = scan_process.communicate() 
		# Block all execution, until the scanning completes.
		scan_process.wait()
		# Returns all output in a dictionary for easy retrieval.
		return {'output':raw_output,'error':raw_error}

	@staticmethod
	def getSSID(raw_cell):
		ssid = raw_cell.split('ESSID:"')[1]
		ssid = ssid.split('"')[0]
		return ssid

	@staticmethod
	def getMAC(raw_cell):
		mac = raw_cell.split('Address: ')[1]
		mac = mac.split('\n')[0]
		return mac

	@staticmethod
	def getQuality(raw_cell):
		#print(raw_cell)
		try:
			quality = raw_cell.split('Quality=')[1]
			quality = quality.split(' ')[0]
		except IndexError:
			quality = '0/100'
		return quality

	@staticmethod
	def getSignalLevel(raw_cell):
		try:
			signal = raw_cell.split('Signal level=')[1]
			signal = signal.split(' ')[0]
			if '/' in signal:
				signal = signal.split('/')[0]
				signal = int(signal)-100
				#signal = int(int(signal)*0.5-95)
			else:
				signal = int(signal)
		except IndexError:
			signal=-90
		return signal

	def parseCell(self, raw_cell):
		cell = {
			'mac': self.getMAC(raw_cell),
			'ssid': self.getSSID(raw_cell),
			'quality': self.getQuality(raw_cell),
			'signal': self.getSignalLevel(raw_cell)
		}
		return cell

	def formatCells(self, raw_cell_string):
		raw_cells = raw_cell_string.decode().split('Cell') # Divide raw string into raw cells.
		#print(raw_cell_string)
		raw_cells.pop(0) # Remove unneccesary "Scan Completed" message.
		if(len(raw_cells) > 0): # Continue execution, if atleast one network is detected.
			# Iterate through raw cells for parsing.
			# Array will hold all parsed cells as dictionaries.
			formatted_cells = [self.parseCell(cell) for cell in raw_cells]
			# Return array of dictionaries, containing cells.
			return formatted_cells
		else:
			print("Networks not detected.")
			return False
		# TODO implement function in ndoe to process this boolean (False)


	@staticmethod
	def filterAccessPoints(all_access_points, network_names):
		focus_points = [] # Array holding the access-points of concern.
		# Iterate throguh all access-points found.
		for point in all_access_points:
			# Check if current AP is in our desired list.
			if point['ssid'] in network_names:
				focus_points.append(point)
		return focus_points
		# TODO implement something incase our desired ones were not found

	@staticmethod
	def filterAccessPointsByMAC(all_access_points, network_macs):
		focus_points = [] # Array holding the access-points of concern.
		# Iterate throguh all access-points found.
		for point in all_access_points:
			# Check if current AP is in our desired list.
			if point['mac'] in network_macs:
				focus_points.append(point)
		return focus_points

	def getAPinfo(self, networks=False, sudo=False):
		# TODO implement error callback if error is raise in subprocess
		# Unparsed access-point listing. AccessPoints are strings.
		raw_scan_output = self.getRawNetworkScan(sudo)['output'] 
		# Parsed access-point listing. Access-points are dictionaries.
		all_access_points = self.formatCells(raw_scan_output)
		# Checks if access-points were found.
		if all_access_points:
			# Checks if specific networks were declared.
			if networks:
				# Return specific access-points found.
				return self.filterAccessPoints(all_access_points, networks)
			else:
				# Return ALL access-points found.
				return all_access_points
		else:
			# No access-points were found. 
			return False
		
	def getAPinfoByMAC(self, networks=False, sudo=False):
		# TODO implement error callback if error is raise in subprocess
		# Unparsed access-point listing. AccessPoints are strings.
		raw_scan_output = self.getRawNetworkScan(sudo)['output'] 
		# Parsed access-point listing. Access-points are dictionaries.
		all_access_points = self.formatCells(raw_scan_output)
		# Checks if access-points were found.
		if all_access_points:
			# Checks if specific networks were declared.
			if networks:
				# Return specific access-points found.
				return self.filterAccessPointsByMAC(all_access_points, networks)
			else:
				# Return ALL access-points found.
				return all_access_points
		else:
			# No access-points were found. 
			return False

class RSSILocalizer():
	
	#signal_attenuation = 4
	#ref_distance = 5
	#ref_signal = -28
	
	def __init__(self,stations):
		self.stations = stations
		
	def getDistanceFromAP(self, station_mac, signal_strength):
		station = self.stations.get(station_mac)
		if station is None:
			return -1
		
		beta_numerator = float(station['reference']['signal']-signal_strength)
		beta_denominator = float(10*station['signalAttenuation'])
		beta = beta_numerator/beta_denominator
		distanceFromAP = round(((10**beta)*station['reference']['distance']),4)

		return distanceFromAP

	def getDistanceFromAllAP(self, signal_data):
		distance_data={}
		for mac, signal in signal_data.items():
			distance_data[mac]=self.getDistanceFromAP(mac,signal)
			
		return distance_data
