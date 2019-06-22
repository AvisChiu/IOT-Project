import frssi


interface = 'wlp3s0'
rssi_scanner = frssi.RSSIScanner(interface)

ssids = ['MD402','MD402_1']

macs = ['8C:3B:AD:22:02:66','00:11:32:9D:2B:30','00:11:32:9D:30:3A','8C:3B:AD:21:FF:66']

ap_info = rssi_scanner.getAPinfoByMAC(networks=macs, sudo=True)

print(ap_info)
signal_data = {}
for ap in ap_info:
	signal_data[ap['mac']] = ap['signal']
	
print(signal_data)

stations = {
	'8C:3B:AD:22:02:66': {
		'x':	13.29,
		'y':	1.05,
		'z':	2.9
	},
	'00:11:32:9D:2B:30': {
		'x':	0.61,
		'y':	7.04,
		'z':	2.9
	},
	'00:11:32:9D:30:3A': {
		'x':	0.82,
		'y':	-0.15,
		'z':	0
	},
	'8C:3B:AD:21:FF:66': {
		'x':	14.24,
		'y':	7.78,
		'z':	0
	},
}


rssi_localizer = frssi.RSSILocalizer(stations)

print(rssi_localizer.getDistanceFromAllAP(signal_data))
