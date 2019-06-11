# -*- coding: utf-8 -*-

import os
import subprocess
import sys
import time

defulat_adb_tool_path = "D:\\developSdk\\Android\\sdk\\platform-tools"


def collect_msg(arg_time, arg_log_path, arg_app_name):
    # 根据应用的包名称 获取CPU温度
    global param_device_id

    cpu_to_filename = os.path.join(
        arg_log_path, param_device_id + "_" + arg_app_name + "_cpu.log"
    )

    # timestamp, cpu-1-name, cpu-2-name ...
    cpu_name_list = ["timestamp"]

    cpu_name_cmd = [
        os.path.join(defulat_adb_tool_path, "adb"),
        "-s",
        param_device_id,
        "shell",
        "cat",
        "/sys/class/thermal/thermal_zone*/type",
    ]

    child = subprocess.Popen(
        cpu_name_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=defulat_adb_tool_path,
    )
    child.wait()
    child_out = child.stdout.readlines()
    child.stdout.close()
    for cpu_name in child_out:
        cpu_name_list.append(bytes.decode(cpu_name).strip())

    with open(cpu_to_filename, "w") as f:
        f.write(",".join(cpu_name_list) + "\n")

    while True:
        now_time = int(time.time())

        cpu_temp_cmd = [
            os.path.join(defulat_adb_tool_path, "adb"),
            "-s",
            param_device_id,
            "shell",
            "cat",
            "/sys/class/thermal/thermal_zone*/temp",
        ]
        child = subprocess.Popen(
            cpu_temp_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=defulat_adb_tool_path,
        )
        child.wait()
        child_out = child.stdout.readlines()
        child.stdout.close()

        cpu_temps = [str(int(now_time))]
        for cpu_temp in child_out:
            cpu_temps.append(str(float(bytes.decode(cpu_temp).strip()) / 1000))

        with open(os.path.join(cpu_to_filename), "a") as f:
            f.write(",".join(cpu_temps) + "\n")

        time.sleep(float(arg_time))


def getparam():
    global param_collect_time
    global param_log_path
    global param_package_name
    global param_device_id
    count = 1
    while count < len(sys.argv):
        if sys.argv[count] == "-h" or sys.argv[count] == "--help":
            print_help()
            sys.exit(0)
        if sys.argv[count] == "--collect-time":
            count += 1
            if count < len(sys.argv):
                param_collect_time = sys.argv[count]

        if sys.argv[count] == "--log-path":
            count += 1
            if count < len(sys.argv):
                param_log_path = sys.argv[count]

        if sys.argv[count] == "--package-name":
            count += 1
            if count < len(sys.argv):
                param_package_name = sys.argv[count]
        if sys.argv[count] == "--device-id":
            count += 1
            if count < len(sys.argv):
                param_device_id = sys.argv[count]
        count += 1


def check_device():
    global param_device_id
    cmd = [os.path.join(defulat_adb_tool_path, "adb"), "devices"]
    child = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=defulat_adb_tool_path
    )
    child.wait()
    child_out = child.stdout.readlines()
    child.stdout.close()

    flag = False
    for item in child_out:
        item = bytes.decode(item)
        if item.find(param_device_id) >= 0 and item.find("offline") < 0:
            flag = True
            break

    return flag


def print_help():
    print(
        "用法 python getAndroidCpu.py --collect-time param-collect-time --log-path param-log-path --device-id param-device-id"
    )
    print("选项：")
    print("\t -h/--help 帮助")
    print("\t --collect-time 信息采集间隔，以秒为单位")
    print("\t --log-path 日志文件的放置位置")
    print("\t --device-id 设备序列号")


if __name__ == "__main__":
    adb_path = os.environ.get("ANDROID_HOME")

    if os.path.isdir(os.path.join(adb_path, "platform-tools")):
        defulat_adb_tool_path = os.path.join(adb_path, "platform-tools")
    else:
        print("请设置‘ANDROID_HOME’环境变量")
        sys.exit(0)

    param_collect_time = ""  # 采集信息时间间隔
    param_log_path = ""  # 日志的放置位置 d:\mi.log
    param_package_name = ""  # 应用的appname
    param_device_id = ""

    if len(sys.argv) <= 3:
        print_help()
        sys.exit(0)

    getparam()

    if param_collect_time == "" or param_log_path == "" or param_device_id == "":
        print("参数不足")
        print_help()
        sys.exit(0)

    if check_device() is False:
        print("设备序列号不存在或离线")
        print_help()
        sys.exit(0)

    collect_msg(param_collect_time, param_log_path, "temperature")
