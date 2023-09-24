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
            {"command": "start", "description": "首次使用向导/显示帮助。"},
            {"command": "done", "description": "结束记录：发送并开始新的记录。"},
            {"command": "check", "description": "检查记录，已有记录。"},
            {"command": "removelast", "description": "删除最后一条记录。"}
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
        params = {'offset': offset, 'timeout': 90}
        r = requests.get(url, params=params, proxies=proxies,timeout=100)
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
            print(f"send to {url}:\n-----message text-----\n{text}\n-----message end-----")
            r = requests.post(url, json=payload, proxies=proxies)            
            if r.status_code == 200:
                print("Message sent; nexttime in 2 seconds...don't stop program!")
                time.sleep(2) 
                continue
            else:
                remaining_messages.append(message)
                print(f"send faild;append to remaining messages:{r.status_code}")
        except Exception as e:
            print(f"Error sending message,append to remaining messages: {e}")
            remaining_messages.append(message)
            print(f"pauses for 10 seconds...don't stop program!")
            time.sleep(10) 

    # 将更新后（或未成功发送的）消息队列保存回文件
    with open('message_queue.json', 'w') as f:
        json.dump(remaining_messages, f)



# 主程序逻辑
def main():
    print("Program started")  # Debugging line
    last_update_id = None
    while True:
        result = set_bot_commands()
        print(f"set menu：{result}")     
        print("Checking for updates...")  # Debugging line
        updates = get_updates(last_update_id)
        if updates and "result" in updates:
           

            print(f"Received updates: {updates}")  # Debugging line
            for update in updates["result"]:
                Messagetype='message'
                if 'edited_message' in update:
                    Messagetype='edited_message'
                last_update_id = update["update_id"] + 1
                chat_id = update[Messagetype]["chat"]["id"]
                message_id = update[Messagetype]["message_id"]
                message_text = update[Messagetype]["text"]
                # 获取当前日期和时间
                current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # 在 message_text 前面加上日期和时间
                message_text_with_datetime = f"#记录成功\n\n```\n{message_text}\n```\n【信息记录时间：{current_datetime}】"

                # 创建唯一标识符
                unique_id = f"{TOKEN}_{chat_id}_{message_id}"            

            

                chat_id_str = str(chat_id)

                if unique_id not in blacklist:
                    # 处理特殊命令
                    if message_text.lower() == "/start":
                        send_message(chat_id_str, f"欢迎使日记助手，你可以直接开始发送要记录的内容.随时可以发送: \n/check 查看已记录的内容，并继续记录。\n /done 记录完毕，把记录发送给您，并开启新的记录。\n /removelast 删除最后一条信息。注意：直接编辑信息并不会修改错误的记录！")   
                        blacklist.append(unique_id)       
                    elif message_text.lower() == "/done":
                        main_text="\n\n".join(user_data[chat_id_str])
                        send_message(chat_id_str, f"#二次确认\n你真的要结束本次记录吗？确认请点击： /confirmdone \n如果不想结束本次记录，直接忽视这条信息、继续发送信息或使用其他指令都可以。")                        
                        blacklist.append(unique_id)
                    elif message_text.lower() == "/confirmdone":
                        main_text="\n\n".join(user_data[chat_id_str])
                        send_message(chat_id_str, f"#结束记录\n以下是记录的全部内容：\n\n```\n{main_text}\n```\n\下次发送消息将开始新的记录.")
                        user_data[chat_id_str] = []
                        blacklist.append(unique_id)
                    elif message_text.lower() == "/check":
                        main_text="\n\n".join(user_data[chat_id_str])
                        send_message(chat_id_str, f"#查看记录\n以下是已记录的全部内容：\n\n```\n{main_text}\n```\n\n发送消息将继续当前的记录.")
                        blacklist.append(unique_id)
                    elif message_text.lower() == "/removelast":
                        if user_data[chat_id_str]:
                            user_data[chat_id_str].pop()
                            send_message(chat_id, "成功删除最后一条消息")
                        else:
                            send_message(chat_id, "没有消息可以删除")
                    else:
                        send_message(chat_id_str, f"{message_text_with_datetime}")
                        if chat_id_str not in user_data:
                            user_data[chat_id_str] = []
                        user_data[chat_id_str].append(message_text)
                        blacklist.append(unique_id)  

                        

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

            
                              
        else:
            print(f"{URL} Received updates: {updates}")
            print("Error or no updates; retrying in 10 seconds...")
            time.sleep(10)  # 等待5秒再重试
        

        print("Process message queue...")
        process_message_queue()
        

# 运行主函数
if __name__ == '__main__':
    main()




