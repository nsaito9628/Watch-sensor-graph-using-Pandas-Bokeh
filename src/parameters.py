import os
import datetime
import paho.mqtt.client as mqtt

#####################################################################
#environment for dashboard system
#####################################################################
client = mqtt.Client(protocol=mqtt.MQTTv311)
HOST = os.environ['HOST_ENDPOINT']  # AWS IoT Endpoint
PORT = 8883  # mqtts port
CACERT = os.environ['CACERT']  # root ca
CLIENTCERT = os.environ['CLIENTCERT']  # certificate
CLIENTKEY = os.environ['CLIENTKEY']  # private key
TOPIC_SENSOR1 = os.environ['TOPIC_SENSOR1']  # topic
#TOPIC_SENSOR2 = os.environ['TOPIC_SENSOR2']
#TOPIC_SENSOR3 = os.environ['TOPIC_SENSOR3']
#TOPIC_SENSOR4 = os.environ['TOPIC_SENSOR4']
TOPIC_DUST = os.environ['TOPIC_DUST']  # topic

MOTION_PIN = 21
DUST_PIN =15

SENSOR_NO = int(os.environ['SENSOR_NO'])

#####################################################################
#environment for cam system
#####################################################################
ACCESS_KEY = os.environ['ACCESS_KEY']
SECRET_KEY = os.environ['SECRET_KEY']
REGION = os.environ['REGION']
#CAM_NO = os.environ['CAM_NO']
S3BUCKET = os.environ['S3BUCKET']
PREFIX_IN1 = os.environ['PREFIX_IN1']
#PREFIX_IN2 = os.environ['PREFIX_IN2']
#PREFIX_IN3 = os.environ['PREFIX_IN3']
#PREFIX_IN4 = os.environ['PREFIX_IN4']

#resolution
#####################################
# 0: 176×144
# 1: 320×240
# 2: 640×480
# 3: 800×600
# 4: 1280×960
#####################################
res = 2 #Default resolution setting 2
resos = ([176, 144, 135, 30, 0.7],
         [320, 240, 230, 30, 1.3], 
         [640, 480, 470, 30, 2], 
         [800, 600, 585, 20, 2.2], 
         [1280, 720, 680, 5, 3.5])#Resolution / recording rate / caption position

#image Threshold when setting differential motion detection as trigger
thd = 30 #Threshold for bit judgment on 256-gradation gray scale
ratio = 0.1 #Threshold for motion detection judgment (area ratio exceeding bit judgment threshold to resolution)

#Video tmp file recording interval
interval = datetime.timedelta(seconds=4) #Record for 4 seconds if the sensor does not detect during the last recording loop
end_interval = datetime.timedelta(seconds=14, microseconds=150000) #Record for 14 seconds if the sensor detects it during the last recording loop