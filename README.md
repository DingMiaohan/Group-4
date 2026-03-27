MQTT IoT Smart Home: Real-time Monitoring for Solitary Elderly

Group 4：Ding Miaohan, Fu Yixin, Niu Yinglin, Meng Junyi, Huang Botao
Development Time：March 2026

1.Project Objective

This project constructs an end-to-edge-cloud collaborative IoT monitoring system based on the MQTT protocol, targeting the safety protection needs of the elderly living alone. The system integrates multi-source sensor data collection (temperature, heart rate, light intensity), leverages ESP32 as the WiFi gateway for MQTT communication, and relies on Eclipse Mosquitto Broker to achieve message routing and distribution. It realizes functions such as real-time environment monitoring, abnormal alarm, and device control, ultimately improving the intelligent safety guarantee level of the elderly's home environment.

2.User Guide

2.(1)Hardware Deployment

  1.Sensor Field Construction: Connect temperature sensor, heart rate sensor, and light sensor to the ESP32 WiFi gateway via corresponding interfaces (I2C/UART) to complete raw data collection.

  2.Gateway Configuration: Program ESP32 to collect sensor data and encapsulate it into MQTT message format, realizing data uplink transmission through WiFi connection.

  3.Actuator Connection: Connect light controller and alert controller to the output end of the MQTT Broker subscription channel to receive control commands and alarm triggers.

2.(2)MQTT Broker & Topic Configuration

  1.Deploy Eclipse Mosquitto Broker, configure port 1883 and enable QoS 0/1/2 message quality levels.

  2.Create core topics based on system logic:

Sensor uplink: elder/sensor/# (temperature/heart rate/light data)

Control downlink: elder/control/# (light/alert control commands)

Status reporting: elder/status/# (network/battery/alarm status)

  3.Start the Broker and ensure message subscription/publishing between each module is normal.

2.(3)Client & System Operation

  1.Start Dashboard Client to subscribe to elder/status/# and elder/sensor/# for real-time data visualization.

  2.Enable Automation Engine to subscribe to control topics, realizing automatic linkage of devices (e.g., light brightness adjustment according to environment).

  3.Start DB Logger to subscribe to sensor data topics, completing persistent storage of monitoring data.

  4.Trigger the Alert Service when receiving alarm messages from elder/status/alarm, and start the Alert Controller for local sound-light alarm.

3.Team Member Responsibilities (Aligned with System Architecture)
Team Member Core Responsibilities & Work Content 
Niu Yinglin System Architecture & Topic DesignOverall modeling of the MQTT message routing architecture; design of three-level topic tree (sensor/control/status) and definition of message format; completion of system topology diagram and flow chart based on the architecture logic. 
Fu Yixin Sensor Data Collection & ESP32 Gateway DevelopmentDriver development of temperature/heart rate/light sensors; data collection and preprocessing (filtering noise, unifying data format); ESP32 WiFi connection and MQTT client programming to realize sensor data publishing. 
Ding Miaohan MQTT Broker Deployment & Message Routing ManagementInstallation, configuration and deployment of Eclipse Mosquitto Broker; debugging of QoS message transmission mechanism; management of topic subscription relationships to ensure stable forwarding of sensor data, control commands and status reports. 
Meng Junyi Actuator Control & Client Application DevelopmentDevelopment of light controller and alert controller logic; implementation of Dashboard Client, DB Logger and Automation Engine functions; debugging of message subscription/publishing between clients and Broker to ensure system linkage. 
Huang Botao System Integration & Comprehensive TestingJoint debugging of each functional module (sensor-gateway-Broker-client); design of test cases for data transmission delay, alarm trigger accuracy and device control responsiveness; sorting and integration of all project documents and PPT materials. 



4. Referenced Resources

  1.Eclipse Foundation. (2024). Mosquitto: An open source MQTT broker. https://mosquitto.org/

  2.Eclipse Foundation. (2023). Paho MQTT Python client library. https://eclipse.dev/paho/clients/python/

  3.OASIS. (2019). MQTT Version 3.1.1 Plus specification. https://docs.oasis-open.org/mqtt/mqtt/v3.1.1/mqtt-v3.1.1.html

  4.Python Software Foundation. (2024). Python 3 documentation. https://docs.python.org/3/

  5.Alghassab, M., & Zualkernan, I. A. (2020). IoT-based smart lighting systems for elderly care: A review. Journal of Ambient Intelligence and Smart Environments, 12(3), 217-234.

  6.Suresh, S., & Priya, R. (2021). Design of motion sensor integrated MQTT-based home automation for elderly safety. International Journal of Advanced Science and Technology, 30(3), 4562-4570.
