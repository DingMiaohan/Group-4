import argparse
import json
import random
import threading
import time
from datetime import datetime

import paho.mqtt.client as mqtt

# =========================
# Mosquitto MQTT 配置（可自行替换）
# =========================
BROKER_HOST = "127.0.0.1"
BROKER_PORT = 1883

# 本地 Mosquitto 默认可不鉴权，按需配置
MQTT_USERNAME = ""
MQTT_PASSWORD = ""

# 固定使用项目约定 Topic（Mosquitto 只负责转发，不需要“控制台主题 ID”那种填法）
# 传感器（运动/光照等）上报 -> 灯控订阅此主题做决策
SENSOR_TOPIC = "env/room/motion"
# 灯控指令 -> 你的灯固件/节点订阅此主题执行开关
LIGHT_CMD_TOPIC = "device/light/control"

# 灯控阈值参数
LUX_THRESHOLD = 35            # 光照阈值，越小越暗
NIGHT_HOUR_START = 22         # 夜间开始小时
NIGHT_HOUR_END = 6            # 夜间结束小时
AUTO_OFF_SECONDS = 90         # 点亮后自动熄灯秒数


def is_night_hour(hour: int) -> bool:
    """判断是否在夜间时段（跨天区间）。"""
    return hour >= NIGHT_HOUR_START or hour < NIGHT_HOUR_END


def create_client(client_id: str) -> mqtt.Client:
    client = mqtt.Client(client_id=client_id, clean_session=True)
    if MQTT_USERNAME or MQTT_PASSWORD:
        client.username_pw_set(username=MQTT_USERNAME or None, password=MQTT_PASSWORD or None)
    return client


def run_sensor_publisher():
    """
    传感器发布端：
    周期性发布人体红外、光照、时间等信息。
    真机接入时，将模拟值替换为真实传感器采集值即可。
    """
    client = create_client("elder_sensor_publisher")
    client.connect(BROKER_HOST, BROKER_PORT, keepalive=60)
    client.loop_start()

    print("传感器发布端已启动，开始发送数据...")
    try:
        while True:
            now = datetime.now()

            # ====== 模拟传感器数据（替换成真实采集）======
            motion_detected = random.random() < 0.25
            lux = random.randint(5, 80)
            # ==========================================

            payload = {
                "device": "bedroom_sensor_1",
                "ts": now.strftime("%Y-%m-%d %H:%M:%S"),
                "hour": now.hour,
                "motion": motion_detected,
                "lux": lux,
            }

            result = client.publish(SENSOR_TOPIC, json.dumps(payload, ensure_ascii=False), qos=0, retain=False)
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                print(f"[PUBLISH] topic={SENSOR_TOPIC} payload={payload}")
            else:
                print(f"[PUBLISH][ERROR] rc={result.rc}")

            time.sleep(3)
    except KeyboardInterrupt:
        print("\n传感器发布端停止。")
    finally:
        client.loop_stop()
        client.disconnect()


class LightController:
    """订阅传感器消息并决策灯光开关。"""

    def __init__(self):
        self.client = create_client("elder_light_subscriber")
        self.light_on = False
        self.auto_off_timer: threading.Timer | None = None

    def connect_and_subscribe(self):
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(BROKER_HOST, BROKER_PORT, keepalive=60)
        self.client.loop_forever()

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            print("灯控订阅端连接成功。")
            client.subscribe(SENSOR_TOPIC, qos=0)
            print(f"已订阅传感器主题: {SENSOR_TOPIC}")
        else:
            print(f"连接失败，rc={rc}")

    def on_message(self, client, userdata, msg):
        try:
            payload = json.loads(msg.payload.decode("utf-8"))
            hour = int(payload.get("hour", datetime.now().hour))
            motion = bool(payload.get("motion", False))
            lux = int(payload.get("lux", 100))

            print(f"[RECV] {payload}")

            # 起夜自动开灯规则：
            # 1) 检测到有人活动
            # 2) 当前为夜间
            # 3) 环境较暗
            if motion and is_night_hour(hour) and lux <= LUX_THRESHOLD:
                self.turn_on_light()
            else:
                print("[RULE] 条件不满足，不开灯。")
        except Exception as e:
            print(f"[ERROR] 消息解析/处理失败: {e}")

    def turn_on_light(self):
        if not self.light_on:
            self.light_on = True
            self.client.publish(LIGHT_CMD_TOPIC, "on", qos=0, retain=False)
            print(f"[LIGHT] 开灯 -> publish {LIGHT_CMD_TOPIC}: on")
        else:
            print("[LIGHT] 灯已开，刷新自动熄灯计时。")

        # 刷新自动关灯定时器
        if self.auto_off_timer is not None:
            self.auto_off_timer.cancel()
        self.auto_off_timer = threading.Timer(AUTO_OFF_SECONDS, self.turn_off_light)
        self.auto_off_timer.start()

    def turn_off_light(self):
        self.light_on = False
        self.client.publish(LIGHT_CMD_TOPIC, "off", qos=0, retain=False)
        print(f"[LIGHT] 自动关灯 -> publish {LIGHT_CMD_TOPIC}: off")


def run_light_subscriber():
    controller = LightController()
    try:
        controller.connect_and_subscribe()
    except KeyboardInterrupt:
        print("\n灯控订阅端停止。")


def main():
    parser = argparse.ArgumentParser(description="MQTT 独居老人起夜自动灯控示例（Mosquitto）")
    parser.add_argument(
        "--role",
        choices=["publisher", "subscriber", "both"],
        default="both",
        help="运行角色: publisher(传感器发布) / subscriber(灯控订阅) / both(同机演示)",
    )
    args = parser.parse_args()

    if args.role == "publisher":
        run_sensor_publisher()
    elif args.role == "subscriber":
        run_light_subscriber()
    else:
        # 同机演示：一个线程跑发布端，主线程跑订阅端
        t = threading.Thread(target=run_sensor_publisher, daemon=True)
        t.start()
        run_light_subscriber()


if __name__ == "__main__":
    main()

