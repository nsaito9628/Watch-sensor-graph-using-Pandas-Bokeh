#!/bin/bash

#/home/pi/ --> mkdir cert && cd cert && cp iot_prov.sh
sudo apt install jq -y
sudo apt update -y
sudo apt upgrade -y

#THING NAME (is same as Project Name)
THING_NAME=$(cat ./iot_prov_config | grep THING_NAME | awk -F'=' '{print $2}')

# create the thing
aws iot create-thing --thing-name ${THING_NAME} | tee create-thing.json
 
# create and download the keys and device certificate
aws iot create-keys-and-certificate --certificate-pem-outfile ${THING_NAME}-certificate.pem.crt --public-key-outfile ${THING_NAME}-public.pem.key --private-key-outfile ${THING_NAME}-private.pem.key --set-as-active | tee create-keys-and-certificate.json
 
# create the thing policy
aws iot create-policy --policy-name ${THING_NAME}_all_access --policy-document '{"Version": "2012-10-17", "Statement": [{"Effect": "Allow", "Action": ["iot:*"], "Resource": ["*"]}]}'
 
# attach the certificate to the thing
CERT_ARN=$(jq -r '.certificateArn' < create-keys-and-certificate.json)
aws iot attach-thing-principal --thing-name ${THING_NAME} --principal ${CERT_ARN}
 
# attach policy to the certificate
aws iot attach-policy --policy-name ${THING_NAME}_all_access --target ${CERT_ARN}
 
# download the amazon root ca
wget https://www.amazontrust.com/repository/AmazonRootCA1.pem
 
# find out what endpoint we need to connect to
echo $(aws iot describe-endpoint --endpoint-type iot:Data-ATS --region ap-northeast-1) >> end_point.json

# creating cron_mod.conf
echo HOST_ENDPOINT=$(jq -r '.endpointAddress' < ./end_point.json) >> cron_mod.conf
echo CACERT=./cert/AmazonRootCA1.pem >> cron_mod.conf
echo CLIENTCERT=./cert/${THING_NAME}-certificate.pem.crt >> cron_mod.conf
echo CLIENTKEY=./cert/${THING_NAME}-private.pem.key >> cron_mod.conf
echo >> cron_mod.conf
echo TOPIC_MOTION=$(cat ./iot_prov_config | grep TOPIC_MOTION | awk -F'=' '{print $2}') >> cron_mod.conf
if [[ $(cat ./iot_prov_config | grep TOPIC_SENSOR1 | awk -F'=' '{print $2}') != "" ]]; then
    echo TOPIC_SENSOR1=$(cat ./iot_prov_config | grep TOPIC_SENSOR1 | awk -F'=' '{print $2}') >> cron_mod.conf
    else
    : #pass
    fi
if [[ $(cat ./iot_prov_config | grep TOPIC_SENSOR2 | awk -F'=' '{print $2}') != "" ]]; then
    echo TOPIC_SENSOR2=$(cat ./iot_prov_config | grep TOPIC_SENSOR2 | awk -F'=' '{print $2}') >> cron_mod.conf
    else
    : #pass
    fi
if [[ $(cat ./iot_prov_config | grep TOPIC_SENSOR3 | awk -F'=' '{print $2}') != "" ]]; then
    echo TOPIC_SENSOR3=$(cat ./iot_prov_config | grep TOPIC_SENSOR3 | awk -F'=' '{print $2}') >> cron_mod.conf
    else
    : #pass
    fi
if [[ $(cat ./iot_prov_config | grep TOPIC_SENSOR4 | awk -F'=' '{print $2}') != "" ]]; then
    echo TOPIC_SENSOR4=$(cat ./iot_prov_config | grep TOPIC_SENSOR4 | awk -F'=' '{print $2}') >> cron_mod.conf
    else
    : #pass
    fi
echo TOPIC_DUST=$(cat ./iot_prov_config | grep TOPIC_DUST | awk -F'=' '{print $2}') >> cron_mod.conf
echo >> cron_mod.conf
echo ACCESS_KEY=$(cat ../.aws/credentials | grep aws_access_key_id | awk -F'= ' '{print $2}') >> cron_mod.conf
echo SECRET_KEY=$(cat ../.aws/credentials | grep aws_secret_access_key | awk -F'= ' '{print $2}') >> cron_mod.conf
echo REGION=$(cat ../.aws/config | grep region | awk -F'= ' '{print $2}') >> cron_mod.conf
echo SENSOR_NO=$(cat ./iot_prov_config | grep SENSOR_NO | awk -F'=' '{print $2}') >> cron_mod.conf
echo S3BUCKET=$(cat ./iot_prov_config | grep S3BUCKET | awk -F'=' '{print $2}') >> cron_mod.conf
echo
if [[ $(cat ./iot_prov_config | grep PREFIX_IN1 | awk -F'=' '{print $2}') != "" ]]; then
    echo PREFIX_IN1=$(cat ./iot_prov_config | grep PREFIX_IN1 | awk -F'=' '{print $2}') >> cron_mod.conf
    else
    : #pass
    fi
if [[ $(cat ./iot_prov_config | grep PREFIX_IN2 | awk -F'=' '{print $2}') != "" ]]; then
    echo PREFIX_IN2=$(cat ./iot_prov_config | grep PREFIX_IN2 | awk -F'=' '{print $2}') >> cron_mod.conf
    else
    : #pass
    fi
if [[ $(cat ./iot_prov_config | grep PREFIX_IN3 | awk -F'=' '{print $2}') != "" ]]; then
    echo PREFIX_IN3=$(cat ./iot_prov_config | grep PREFIX_IN3 | awk -F'=' '{print $2}') >> cron_mod.conf
    else
    : #pass
    fi
if [[ $(cat ./iot_prov_config | grep PREFIX_IN4 | awk -F'=' '{print $2}') != "" ]]; then
    echo PREFIX_IN4=$(cat ./iot_prov_config | grep PREFIX_IN4 | awk -F'=' '{print $2}') >> cron_mod.conf
    else
    : #pass
    fi

echo >> cron_mod.conf
echo @reboot . ~/.profile >> cron_mod.conf
if [ ! -e /home/pi/motion_detect_serverless.py ]; then
    echo
    else 
    echo @reboot python /home/pi/motion_detect_serverless.py >> cron_mod.conf
    fi
if [ ! -e /home/pi/motion_detect.py ]; then
    echo
    else 
    echo @reboot python /home/pi/motion_detect.py >> cron_mod.conf
    fi
if [ ! -e /home/pi/dust_detect.py ]; then
    echo
    else 
    echo @reboot python /home/pi/dust_detect.py >> cron_mod.conf
    fi
if [ ! -e /home/pi/emr_rec.py ]; then
    echo
    else 
    echo @reboot python /home/pi/emr_rec.py >> cron_mod.conf
    fi


# adding .profile
echo >> ../.profile
echo export HOST_ENDPOINT=$(jq -r '.endpointAddress' < ./end_point.json) >> ../.profile
echo export CACERT=./cert/AmazonRootCA1.pem >> ../.profile
echo export CLIENTCERT=./cert/${THING_NAME}-certificate.pem.crt >> ../.profile
echo export CLIENTKEY=./cert/${THING_NAME}-private.pem.key >> ../.profile
echo >> ../.profile
echo export TOPIC_MOTION=myroom/motion >> ../.profile
if [[ $(cat ./iot_prov_config | grep TOPIC_SENSOR1 | awk -F'=' '{print $2}') != "" ]]; then
    echo export TOPIC_SENSOR1=$(cat ./iot_prov_config | grep TOPIC_SENSOR1 | awk -F'=' '{print $2}') >> ../.profile
    else
    : #pass
    fi
if [[ $(cat ./iot_prov_config | grep TOPIC_SENSOR2 | awk -F'=' '{print $2}') != "" ]]; then
    echo export TOPIC_SENSOR2=$(cat ./iot_prov_config | grep TOPIC_SENSOR2 | awk -F'=' '{print $2}') >> ../.profile
    else
    : #pass
    fi
if [[ $(cat ./iot_prov_config | grep TOPIC_SENSOR3 | awk -F'=' '{print $2}') != "" ]]; then
    echo export TOPIC_SENSOR3=$(cat ./iot_prov_config | grep TOPIC_SENSOR3 | awk -F'=' '{print $2}') >> ../.profile
    else
    : #pass
    fi
if [[ $(cat ./iot_prov_config | grep TOPIC_SENSOR4 | awk -F'=' '{print $2}') != "" ]]; then
    echo export TOPIC_SENSOR4=$(cat ./iot_prov_config | grep TOPIC_SENSOR4 | awk -F'=' '{print $2}') >> ../.profile
    else
    : #pass
    fi
echo export TOPIC_DUST=myroom/dust >> ../.profile
echo >> ../.profile
echo export ACCESS_KEY=$(cat ../.aws/credentials | grep aws_access_key_id | awk -F'= ' '{print $2}') >> ../.profile
echo export SECRET_KEY=$(cat ../.aws/credentials | grep aws_secret_access_key | awk -F'= ' '{print $2}') >> ../.profile
echo export REGION=$(cat ../.aws/config | grep region | awk -F'= ' '{print $2}') >> ../.profile
echo export SENSOR_NO=$(cat ./iot_prov_config | grep SENSOR_NO | awk -F'=' '{print $2}') >> ../.profile
echo export S3BUCKET=$(cat ./iot_prov_config | grep S3BUCKET | awk -F'=' '{print $2}') >> ../.profile
if [[ $(cat ./iot_prov_config | grep PREFIX_IN1 | awk -F'=' '{print $2}') != "" ]]; then
    echo export PREFIX_IN1=$(cat ./iot_prov_config | grep PREFIX_IN1 | awk -F'=' '{print $2}') >> ../.profile
    else
    : #pass
    fi
if [[ $(cat ./iot_prov_config | grep PREFIX_IN2 | awk -F'=' '{print $2}') != "" ]]; then
    export echo PREFIX_IN2=$(cat ./iot_prov_config | grep PREFIX_IN2 | awk -F'=' '{print $2}') >> ../.profile
    else
    : #pass
    fi
if [[ $(cat ./iot_prov_config | grep PREFIX_IN3 | awk -F'=' '{print $2}') != "" ]]; then
    export echo PREFIX_IN3=$(cat ./iot_prov_config | grep PREFIX_IN3 | awk -F'=' '{print $2}') >> ../.profile
    else
    : #pass
    fi
if [[ $(cat ./iot_prov_config | grep PREFIX_IN4 | awk -F'=' '{print $2}') != "" ]]; then
    export echo PREFIX_IN4=$(cat ./iot_prov_config | grep PREFIX_IN4 | awk -F'=' '{print $2}') >> ../.profile
    else
    : #pass
    fi

crontab ./cron_mod.conf
