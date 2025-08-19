import sys, time, numpy as np
from yoctopuce.yocto_api import *
from yoctopuce.yocto_magnetometer import *
from yoctopuce.yocto_tilt import *
from yoctopuce.yocto_temperature import *
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS

start = time.time()
now = start
url = "http://yemonitor.colorado.edu:8086"
token = "yelabtoken"
org = "yelab"
bucket = "yoctopuce_sensor" # If bucket not exists, create it from the database UI.
client = InfluxDBClient(url=url, token=token, org=org)
write_api = client.write_api(write_options=SYNCHRONOUS)

sensor1_serial = 'Y3DMK001-BA98C'
sensor2_serial = 'YCLINOM1-2D5B79'
errmsg = YRefParam()
# Setup the API to use local USB devices
if YAPI.RegisterHub("admin:698gang!@192.168.1.126", errmsg) != YAPI.SUCCESS:
    sys.exit("init error " + str(errmsg))

sensor1_magnetometer = YMagnetometer.FindMagnetometer(sensor1_serial+'.magnetometer')
sensor1_tilt1 = YTilt.FindTilt(sensor1_serial+'.tilt1')
sensor1_tilt2 = YTilt.FindTilt(sensor1_serial+'.tilt2')
sensor2_tilt1 = YTilt.FindTilt(sensor2_serial+'.tilt1')
sensor2_tilt2 = YTilt.FindTilt(sensor2_serial+'.tilt2')
sensor2_tilt3 = YTilt.FindTilt(sensor2_serial+'.tilt3')
sensor2_temperature = YTemperature.FindTemperature(sensor2_serial+'.temperature')

sensor1_magnetometer_Xvalue = []
sensor1_magnetometer_Yvalue = []
sensor1_magnetometer_Zvalue = []
sensor1_tilt1_value = []
sensor1_tilt2_value = []
sensor2_tilt1_value = []
sensor2_tilt2_value = []
sensor2_tilt3_value = []
sensor2_temperature_value = []

while now-start<40:
    if sensor1_magnetometer.isOnline():
        sensor1_magnetometer_Xvalue.append(sensor1_magnetometer.get_xValue())
        sensor1_magnetometer_Yvalue.append(sensor1_magnetometer.get_yValue())
        sensor1_magnetometer_Zvalue.append(sensor1_magnetometer.get_zValue())
        sensor1_tilt1_value.append(sensor1_tilt1.get_currentValue())
        sensor1_tilt2_value.append(sensor1_tilt2.get_currentValue())
    # else:
    #     print(sensor1_serial + " not connected (check identification and USB cable)")

    if sensor2_temperature.isOnline():
        sensor2_tilt1_value.append(sensor2_tilt1.get_currentValue())
        sensor2_tilt2_value.append(sensor2_tilt2.get_currentValue())
        sensor2_tilt3_value.append(sensor2_tilt3.get_currentValue())
        sensor2_temperature_value.append(sensor2_temperature.get_currentValue())
    # else:
    #     print(sensor2_serial + " not connected (check identification and USB cable)")
    now=time.time()
YAPI.FreeAPI()

if len(sensor1_magnetometer_Xvalue)>0:
    message_sensor1_mean = (
        f"yoctopuce_sensor,host=mean "
        f"sensor1_magnetometer_X={np.mean(np.array(sensor1_magnetometer_Xvalue))},"
        f"sensor1_magnetometer_Y={np.mean(np.array(sensor1_magnetometer_Yvalue))},"
        f"sensor1_magnetometer_Z={np.mean(np.array(sensor1_magnetometer_Zvalue))},"
        f"sensor1_tilt1={np.mean(np.array(sensor1_tilt1_value))},"
        f"sensor1_tilt2={np.mean(np.array(sensor1_tilt2_value))}"
    )
    write_api.write(bucket, org, message_sensor1_mean)
if len(sensor2_temperature_value)>0:
    message_sensor2_mean = (
        f"yoctopuce_sensor,host=mean "
        f"sensor2_tilt1={np.mean(np.array(sensor2_tilt1_value))},"
        f"sensor2_tilt2={np.mean(np.array(sensor2_tilt2_value))},"
        f"sensor2_tilt3={np.mean(np.array(sensor2_tilt3_value))},"
        f"sensor2_temperature={np.mean(np.array(sensor2_temperature_value))}"
    )
    write_api.write(bucket, org, message_sensor2_mean)
if len(sensor1_magnetometer_Xvalue)>1:
    message_sensor1_std = (
        f"yoctopuce_sensor,host=std "
        f"sensor1_magnetometer_X={np.std(np.array(sensor1_magnetometer_Xvalue),ddof=1)},"
        f"sensor1_magnetometer_Y={np.std(np.array(sensor1_magnetometer_Yvalue),ddof=1)},"
        f"sensor1_magnetometer_Z={np.std(np.array(sensor1_magnetometer_Zvalue),ddof=1)},"
        f"sensor1_tilt1={np.std(np.array(sensor1_tilt1_value),ddof=1)},"
        f"sensor1_tilt2={np.std(np.array(sensor1_tilt2_value),ddof=1)}"
    )
    write_api.write(bucket, org, message_sensor1_std)
if len(sensor2_temperature_value)>1:
    message_sensor2_std = (
        f"yoctopuce_sensor,host=std "
        f"sensor2_tilt1={np.std(np.array(sensor2_tilt1_value),ddof=1)},"
        f"sensor2_tilt2={np.std(np.array(sensor2_tilt2_value),ddof=1)},"
        f"sensor2_tilt3={np.std(np.array(sensor2_tilt3_value),ddof=1)},"
        f"sensor2_temperature={np.std(np.array(sensor2_temperature_value),ddof=1)}"
    )
    write_api.write(bucket, org, message_sensor2_std)
client.close()