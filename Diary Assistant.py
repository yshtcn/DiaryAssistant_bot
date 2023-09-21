# 修改代码以记录黑名单而非删除消息

# 示例代码（请在本地环境中运行）
import json
import requests
import time
from datetime import datetime
import os
import json

# 配置代理
proxies = {
    'http': 'http://127.0.0.1:7890',
    'https': 'http://127.0.0.1:7890'
}

TOKEN = None

# 示范Token
example_token = "Your_Token_Here"

# 定义配置文件名
config_filename = "bot_config.json"

# 检查配置文件是否存在
config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), config_filename)

if os.path.exists(config_path):
    # 读取配置文件
    with open(config_path, 'r') as f:
        config = json.load(f)
    TOKEN = config.get("TOKEN", "")
    
    # 检查Token是否已设置
    if TOKEN == example_token:
        print("Please update your bot token in the config file.")
        exit(1)
else:
    # 如果配置文件不存在，则创建一个新的配置文件并写入示范Token
    config = {"TOKEN": example_token}
    with open(config_path, 'w') as f:
        json.dump(config, f)
    print(f"Config file created at {config_path}. Please update your bot token.")
    exit(1)

URL = f"https://api.telegram.org/bot{TOKEN}/"

# 尝试从文件中加载已有数据
try:
    with open('user_data.json', 'r') as f:
        user_data = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    user_data = {}

def set_bot_commands():
    try:
        set_commands_url = URL + "setMyCommands"
        commands = [
            {"command": "done", "description": "结束记录：发送并开始新的记录."},
            {"command": "check", "description": "检查记录，已有记录。"}
        ]
        response = requests.post(set_commands_url, json={"commands": commands}, proxies=proxies)
        response.raise_for_status()  # 如果响应状态码不是200，引发HTTPError异常

        return response.json()
    except requests.HTTPError as http_err:
        return f"HTTP error occurred: {http_err}"
    except Exception as err:
        return f"An error occurred: {err}"


# 尝试从文件中加载黑名单
try:
    with open('blacklist.json', 'r') as f:
        blacklist = json.load(f)
except FileNotFoundError:
    blacklist = []


# 获取更新
def get_updates(offset=None):
    try:
        url = URL + "getUpdates"
        params = {'offset': offset}
        r = requests.get(url, params=params, proxies=proxies)
        return r.json()
    except Exception as e:
        print(f"Error getting updates: {e}")
        return None

# 发送消息
def send_message(chat_id, text):
    try:
        # 尝试从文件中加载消息队列
        try:
            with open('message_queue.json', 'r') as f:
                message_queue = json.load(f)
        except FileNotFoundError:
            message_queue = []
        
        # 将新消息添加到队列
        message_queue.append({'chat_id': chat_id, 'text': text})
        
        # 将更新后的消息队列保存回文件
        with open('message_queue.json', 'w') as f:
            json.dump(message_queue, f)
    except Exception as e:
        print(f"Error queuing message: {e}")

def funcion_send_message(chat_id, text, reply_markup=None):
    url = URL + "sendMessage"
    params = {'chat_id': chat_id, 'text': text, 'reply_markup': reply_markup}
    requests.post(url, params, proxies=proxies)

def process_message_queue():
    # 尝试从文件中加载消息队列
    try:
        with open('message_queue.json', 'r') as f:
            message_queue = json.load(f)
    except FileNotFoundError:
        message_queue = []
        
    # 遍历消息队列，尝试发送消息
    remaining_messages = []
    for message in message_queue:
        chat_id = message['chat_id']
        text = message['text']
        try:
            url = URL + "sendMessage"
            payload = {'chat_id': chat_id, 'text': text,'parse_mode': 'Markdown'}
            r = requests.post(url, json=payload, proxies=proxies)
            if r.status_code == 200:
                continue
            else:
                remaining_messages.append(message)
        except Exception as e:
            print(f"Error sending message: {e}")
            remaining_messages.append(message)

    # 将更新后（或未成功发送的）消息队列保存回文件
    with open('message_queue.json', 'w') as f:
        json.dump(remaining_messages, f)



# 主程序逻辑
def main():
    print("Program started")  # Debugging line
    last_update_id = None
    while True:     

        print("Checking for updates...")  # Debugging line
        updates = get_updates(last_update_id)
        if updates and "result" in updates:
            print(f"Received updates: {updates}")  # Debugging line
            for update in updates["result"]:
                last_update_id = update["update_id"] + 1
                chat_id = update["message"]["chat"]["id"]
                message_id = update["message"]["message_id"]
                message_text = update["message"]["text"]
                # 获取当前日期和时间
                current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # 在 message_text 前面加上日期和时间
                message_text_with_datetime = f"【记录时间：{current_datetime}】\n{message_text}"

                # 创建唯一标识符
                unique_id = f"{TOKEN}_{chat_id}_{message_id}"            

            

                chat_id_str = str(chat_id)

                if unique_id not in blacklist:
                    # 处理“done”命令
                    if message_text.lower() == "/start":
                        result = set_bot_commands()
                        print(f"set menu：{result}")
                        send_message(chat_id_str, f"欢迎使日记助手，你可以直接开始发送要记录的内容.随时可以发送 /check 查看已发送的内容。记录完毕可以发送 /done ，我会把所有内容整合在一起发送给您。")   
                        blacklist.append(unique_id)       
                    elif message_text.lower() == "/done":
                        main_text="\n\n".join(user_data[chat_id_str])
                        send_message(chat_id_str, f"#最终内容\n以下是记录的全部内容：\n\n```\n{main_text}\n```\n\n继续发送将开始新的记录。")
                        user_data[chat_id_str] = []
                        blacklist.append(unique_id)
                    elif message_text.lower() == "/check":
                        main_text="\n\n".join(user_data[chat_id_str])
                        send_message(chat_id_str, f"#当前内容\n以下是已记录的全部内容：\n\n```\n{main_text}\n```\n\n继续发送将当前的记录。")
                        blacklist.append(unique_id)
                    else:
                        send_message(chat_id_str, f"{message_text_with_datetime}")
                        if chat_id_str not in user_data:
                            user_data[chat_id_str] = []
                        user_data[chat_id_str].append(message_text)
                        blacklist.append(unique_id)  # 添加到黑名单

                        

                    # 保存数据到文件
                    with open('user_data.json', 'w') as f:
                        json.dump(user_data, f)
                    with open('blacklist.json', 'w') as f:
                        json.dump(blacklist, f)

                
                # 保存数据到文件
                with open('user_data.json', 'w') as f:
                    json.dump(user_data, f)
                with open('blacklist.json', 'w') as f:
                    json.dump(blacklist, f)

                print("Process message queue...")
                process_message_queue()                
        else:
            print(f"{URL} Received updates: {updates}")
            print("Error or no updates; retrying in 30 seconds...")
            time.sleep(30)  # 等待5秒再重试
        
        print("process message queue...")
        process_message_queue()
        # 每30s检查一次
        print("Next time in 30 seconds...")
        time.sleep(30)

# 运行主函数
if __name__ == '__main__':
    main()




