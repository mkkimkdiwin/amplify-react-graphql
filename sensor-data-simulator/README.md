# sensor-data-simulator

## with python v2 SDK (default) - https://github.com/aws/aws-iot-device-sdk-python-v2.git

* pubsub_simulator_training.py : data generator for training
`pubsub_simulator_training_v2.py --endpoint awaztwvri1f9k-ats.iot.us-east-1.amazonaws.com --ca_file root-CA.crt --cert 56d1a0401f-certificate.pem.crt --key 56d1a0401f-private.pem.key --client_id MyThing --topic iot/sensors`

* pubsub_simulator_inference.py : data generator for inference
`pubsub_simulator_inference_v2.py --endpoint awaztwvri1f9k-ats.iot.us-east-1.amazonaws.com --ca_file root-CA.crt --cert 56d1a0401f-certificate.pem.crt --key 56d1a0401f-private.pem.key --client_id MyThing --topic iot/sensors`


## with python v1 SDK
* pubsub_simulator_training.py : data generator for training
`pubsub_simulator_training.py --endpoint awaztwvri1f9k-ats.iot.us-east-1.amazonaws.com --cert 56d1a0401f-certificate.pem.crt --key 56d1a0401f-private.pem.key --topic iot/sensors`

* pubsub_simulator_inference.py : data generator for inference
`pubsub_simulator_inference.py --endpoint awaztwvri1f9k-ats.iot.us-east-1.amazonaws.com --cert 56d1a0401f-certificate.pem.crt --key 56d1a0401f-private.pem.key --topic iot/sensors`