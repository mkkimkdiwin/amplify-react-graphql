'''
/*
 * Copyright 2010-2017 Amazon.com, Inc. or its affiliates. All Rights Reserved.
 *
 * Licensed under the Apache License, Version 2.0 (the "License").
 * You may not use this file except in compliance with the License.
 * A copy of the License is located at
 *
 *  http://aws.amazon.com/apache2.0
 *
 * or in the "license" file accompanying this file. This file is distributed
 * on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
 * express or implied. See the License for the specific language governing
 * permissions and limitations under the License.
 */
 '''

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import AWSIoTPythonSDK.exception
import logging
import time
import argparse
import json
import random
from datetime import datetime
import data_simulator as ds
import pprint

AllowedActions = ['both', 'publish', 'subscribe']

# Custom MQTT message callback
def customCallback(client, userdata, message):
    print("Received a new message: ")
    print(message.payload)
    print("from topic: ")
    print(message.topic)
    print("--------------\n\n")


# Read in command-line parameters
parser = argparse.ArgumentParser()
parser.add_argument("-e", "--endpoint", default="awaztwvri1f9k-ats.iot.us-east-1.amazonaws.com", action="store", dest="host", help="Your AWS IoT custom endpoint")
parser.add_argument("-r", "--rootCA", default="AmazonRootCA1.pem", action="store", dest="rootCAPath", help="Root CA file path")
parser.add_argument("-c", "--cert", default="56d1a0401f-certificate.pem.crt", action="store", dest="certificatePath", help="Certificate file path")
parser.add_argument("-k", "--key", default="56d1a0401f-private.pem.key", action="store", dest="privateKeyPath", help="Private key file path")
parser.add_argument("-p", "--port", default=8883, action="store", dest="port", type=int, help="Port number override")
parser.add_argument("-w", "--websocket", action="store_true", dest="useWebsocket", default=False,
                    help="Use MQTT over WebSocket")
parser.add_argument("-id", "--clientId", action="store", dest="clientId", default="TurckPLC",
                    help="Targeted client id")
parser.add_argument("-t", "--topic", action="store", dest="topic", default="turck/inference", help="Targeted topic")
parser.add_argument("-m", "--mode", action="store", dest="mode", default="both",
                    help="Operation modes: %s"%str(AllowedActions))
parser.add_argument("-M", "--message", action="store", dest="message", default="Hello World!",
                    help="Message to publish")

args = parser.parse_args()
host = args.host
rootCAPath = args.rootCAPath
certificatePath = args.certificatePath
privateKeyPath = args.privateKeyPath
port = args.port
useWebsocket = args.useWebsocket
clientId = args.clientId
topic = args.topic

if args.mode not in AllowedActions:
    parser.error("Unknown --mode option %s. Must be one of %s" % (args.mode, str(AllowedActions)))
    exit(2)

if args.useWebsocket and args.certificatePath and args.privateKeyPath:
    parser.error("X.509 cert authentication and WebSocket are mutual exclusive. Please pick one.")
    exit(2)

if not args.useWebsocket and (not args.certificatePath or not args.privateKeyPath):
    parser.error("Missing credentials for authentication.")
    exit(2)

# Port defaults
if args.useWebsocket and not args.port:  # When no port override for WebSocket, default to 443
    port = 443
if not args.useWebsocket and not args.port:  # When no port override for non-WebSocket, default to 8883
    port = 8883

# Configure logging
logger = logging.getLogger("AWSIoTPythonSDK.core")
logger.setLevel(logging.DEBUG)
streamHandler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
streamHandler.setFormatter(formatter)
logger.addHandler(streamHandler)

# Init AWSIoTMQTTClient
myAWSIoTMQTTClient = None
if useWebsocket:
    myAWSIoTMQTTClient = AWSIoTMQTTClient(clientId, useWebsocket=True)
    myAWSIoTMQTTClient.configureEndpoint(host, port)
    myAWSIoTMQTTClient.configureCredentials(rootCAPath)
else:
    myAWSIoTMQTTClient = AWSIoTMQTTClient(clientId)
    myAWSIoTMQTTClient.configureEndpoint(host, port)
    myAWSIoTMQTTClient.configureCredentials(rootCAPath, privateKeyPath, certificatePath)

# AWSIoTMQTTClient connection configuration
myAWSIoTMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
myAWSIoTMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
myAWSIoTMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
myAWSIoTMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
myAWSIoTMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec

# Connect and subscribe to AWS IoT
myAWSIoTMQTTClient.connect()
if args.mode == 'both' or args.mode == 'subscribe':
    myAWSIoTMQTTClient.subscribe(topic, 1, customCallback)
time.sleep(2)

# Publish to the same topic in a loop forever
loopCount = 0
config_data = ds.load_config("iot-app-hol-online/sensor-data-simulator/config.json")

while True:
    if args.mode == 'both' or args.mode == 'publish':

        message = {}
        if loopCount % 60 == 0:

            loopCount = 0

            message["rVibration_Temp"] = float(90)
            message["rVibration_Z_RMS_Velocity"] = float(130)
            message["rVibration_X_RMS_Velocity"] = float(10)
            message["wRMSCurrent"] = float(111)
            message["wCurrentLoad"] = float(111)
            message["wEncoderVelocity"] = float(34)
        else:
            message["rVibration_Temp"] = round(random.uniform(40, 50),2)
            message["rVibration_Z_RMS_Velocity"] = round(random.uniform(80, 100),2)
            message["rVibration_X_RMS_Velocity"] = round(random.uniform(80, 100),2)
            message["wRMSCurrent"] = round(random.uniform(40, 50),2)
            message["wCurrentLoad"] = round(random.uniform(40, 50),2)
            message["wEncoderVelocity"] = round(random.uniform(20, 30),2)

        config_label = config_data['label']
        message[config_label['name']] = float(ds.generate_label(config_label, message))
        message['sDateTime'] = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]

        t = datetime.utcnow()
        timeInSeconds = int((t-datetime(1970,1,1)).total_seconds())
        message['timeInSeconds'] = timeInSeconds

        # pprint.pprint(message)
        messageJson = json.dumps(message)

        try:
            myAWSIoTMQTTClient.publish(topic, messageJson, 1)
        except AWSIoTPythonSDK.exception.AWSIoTExceptions.publishTimeoutException:
            time.sleep(2)
            # Connect and subscribe to AWS IoT
            print('RETRY: Connect and subscribe to AWS IoT')
            myAWSIoTMQTTClient.connect()
            if args.mode == 'both' or args.mode == 'subscribe':
                myAWSIoTMQTTClient.subscribe(topic, 1, customCallback)
            time.sleep(2)
            myAWSIoTMQTTClient.publish(topic, messageJson, 1)

        if args.mode == 'publish':
            print('Published topic %s: %s\n' % (topic, messageJson))

        loopCount += 1
    time.sleep(1)
