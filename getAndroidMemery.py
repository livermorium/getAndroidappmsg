# -*- coding: utf-8 -*-

import os
import subprocess
import sys
import time

defulat_adb_tool_path = "D:\\developSdk\\Android\\sdk\\platform-tools"


def collect_msg(arg_time, arg_log_path, arg_app_name):
    # 根据应用的包名称 获取CPU以及内存占用+
    global param_device_id

    mem_to_filename = os.path.join(
        arg_log_path, param_device_id + "_" + arg_app_name + "_memory.log"
    )

    cpu_memery_cmd = [
        os.path.join(defulat_adb_tool_path, "adb"),
        "-s",
        param_device_id,
        "shell",
        "cat",
        "/proc/meminfo",
        "|",
        "grep",
        "MemTotal",
    ]
    child = subprocess.Popen(
        cpu_memery_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=defulat_adb_tool_path,
    )

    child.wait()
    child_out = child.stdout.readlines()
    child.stdout.close()

    # MemTotal:        2006852 kB
    mem_total = int(bytes.decode(child_out[0]).split(":")[1].split()[0].strip())

    with open(mem_to_filename, "w") as f:
        f.write("timestamp,mem-usage-percent,mem-usage\n")

    while 1:
        now_time = int(time.time())
        cpu_memery_cmd = [
            os.path.join(defulat_adb_tool_path, "adb"),
            "-s",
            param_device_id,
            "shell",
            "top",
            "-m",
            "10",
            "-n",
            "1",
        ]
        child = subprocess.Popen(
            cpu_memery_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=defulat_adb_tool_path,
        )

        child.wait()
        child_out = child.stdout.readlines()
        child.stdout.close()

        for item in child_out:
            item = bytes.decode(item)
            if item.find(arg_app_name) > 0:
                mem_usage = int(item.split("K")[1].strip())
                mem_usage_percent = mem_usage / mem_total * 100
                with open(mem_to_filename, "a") as f:

                    f.write(f"{now_time},{mem_usage_percent:.2f},{mem_usage}\n")

                break

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
        "用法 python getAndroidCpu.py --collect-time param --log-path param --package-name param --device-id param"
    )
    print("选项：")
    print("\t -h/--help 帮助")
    print("\t --collect-time 信息采集间隔，以秒为单位")
    print("\t --log-path 日志文件的放置位置")
    print("\t --package-name 应用的包名")
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

    if (
        param_collect_time == ""
        or param_log_path == ""
        or param_package_name == ""
        or param_device_id == ""
    ):
        print("参数不足")
        print_help()
        sys.exit(0)

    if check_device() is False:
        print("设备序列号不存在或离线")
        print_help()
        sys.exit(0)

    collect_msg(param_collect_time, param_log_path, param_package_name)
