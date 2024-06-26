import json
import requests
import time
from datetime import datetime
import os
import json
import sys
from tqdm import tqdm

proxies = None

TOKEN = None



# 定义当前脚本所在目录
current_dir = os.path.dirname(os.path.abspath(__file__))
#如果是frozen的使用exe所在的目录
if getattr(sys, 'frozen', False):
    current_dir = os.path.dirname(sys.executable)
#如果是docker，设置为data目录
if os.path.exists('/.dockerenv'):
    current_dir = '/data'


# 定义配置文件名
config_filename = "bot_config.json"
blacklist_filename="blacklist.json"
message_queue_filename="message_queue.json"
user_data_filename="user_data.json"


# 检查配置文件是否存在
config_path = os.path.join(current_dir, config_filename)
print(f"Config file path: {config_path}")

if os.path.exists(config_path):
    # 读取配置文件
    with open(config_path, 'r') as f:
        config = json.load(f)
    TOKEN = config.get("TOKEN", "")
    proxies_config = config.get("PROXIES", {})
    
    # 检查Token是否已设置
    if not TOKEN:
        print("Please set your bot token in the config file.")
        input("Press any key to exit...")
        exit(1)
    #或者检查TOKEN是否等于”Your_Token_Here“
    elif TOKEN == "Your_Token_Here":  
        print("Please set your bot token in the config file.")
        input("Press any key to exit...")
        exit(1)
else:
    # 如果配置文件不存在，则创建一个新的配置文件并写入示范Token和示范代理
    config = {
        "TOKEN": "Your_Token_Here",
        "PROXIES": {
            "http": "http://127.0.0.1:7890",
            "https": "http://127.0.0.1:7890"
        }
    }
    # 将config对象转换为格式化的JSON字符串
    config_str = json.dumps(config, indent=4) 
    print(config_str)
    with open(config_path, 'w') as f:
        f.write(config_str)
    print(f"Config file created at {config_path}. Please set your bot token.")
    # 等待用户按任意键退出
    input("Press any key to exit...")
    exit(1)

# 设置代理
if proxies_config:
    proxies = {
        'http': proxies_config.get('http', ''),
        'https': proxies_config.get('https', '')
    }
else:
    proxies = None

URL = f"https://api.telegram.org/bot{TOKEN}/"

# 尝试从文件中加载已有数据
try:
    with open(os.path.join(current_dir, user_data_filename), 'r') as f:
        user_data = json.load(f)
    print(f"User data loaded: {user_data}")
except (FileNotFoundError, json.JSONDecodeError):
    print("No user data found; starting with empty data.")
    user_data = {}

# 尝试从文件中加载黑名单
try:
    with open(os.path.join(current_dir, blacklist_filename), 'r') as f:
        blacklist = json.load(f)
    print(f"Blacklist loaded: {blacklist}")
except FileNotFoundError:
    blacklist = []
    print("No blacklist found; starting with empty blacklist.")

def set_bot_commands():
    try:
        set_commands_url = URL + "setMyCommands"
        commands = [
            {"command": "/today", "description": "发送今天的日期"},
            {"command": "/nowstart", "description": "发送现在的时间作为开始时间"},
            {"command": "/nowend", "description": "发送现在的时间作为结束时间"},
            {"command": "/removelast", "description": "删除最后记录"},
            {"command": "/check", "description": "检查记录"},
            {"command": "/done", "description": "结束记录"}, 
            # {"command": "/prompt", "description": "GPT分次对话提示语"},
            {"command": "/stopprompt", "description": "GPT分次结束对话提示语"},          
            {"command": "/start", "description": "首次使用"}
        ]
        response = requests.post(set_commands_url, json={"commands": commands}, proxies=proxies)
        response.raise_for_status()  # 如果响应状态码不是200，引发HTTPError异常

        return response.json()
    except requests.HTTPError as http_err:
        return f"HTTP error occurred: {http_err} - {response.text}"
    except Exception as err:
        return f"An error occurred: {err}"


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
            with open(os.path.join(current_dir, message_queue_filename), 'r') as f:
                message_queue = json.load(f)
        except FileNotFoundError:
            message_queue = []
        
        # 将新消息添加到队列
        message_queue.append({'chat_id': chat_id, 'text': text})
        
        # 将更新后的消息队列保存回文件
        with open(os.path.join(current_dir, message_queue_filename), 'w') as f:
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
        with open(os.path.join(current_dir, message_queue_filename), 'r') as f:
            message_queue = json.load(f)
    except FileNotFoundError:
        message_queue = []
        
    # 遍历消息队列，尝试发送消息
    remaining_messages = []
    for message in tqdm(message_queue,desc="send message loop:"):        
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
    with open(os.path.join(current_dir, message_queue_filename), 'w') as f:
        json.dump(remaining_messages, f)



# 主程序逻辑
def main():
    print("Program started") 
    last_update_id = None
    while True:
        print("Process message queue...") 
        process_message_queue()
        result = set_bot_commands()
        print(f"set menu：{result}")     
        print("Check updates,Waiting for response...")  
        updates = get_updates(last_update_id)
        if updates and "result" in updates:          

            print(f"Received updates: {updates}")  
            for update in tqdm(updates["result"],desc="get result loop:"):
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
                message_text_with_datetime = f"#记录成功\n---\n```\n{message_text}\n```\n---\n【信息记录时间：{current_datetime}】"

                # 创建唯一标识符
                unique_id = f"{TOKEN}_{chat_id}_{message_id}"            

            

                chat_id_str = str(chat_id)

                if unique_id not in blacklist:
                    # 处理特殊命令
                    if message_text.lower() == "/start":
                        send_message(chat_id_str, f"#使用帮助\n---\n欢迎使用日记和日程助手机器人，你可以直接开始发送要记录的文字内容。以下是机器人可用指令: \n/check #查看记录 \n/done #结束记录 \n/stopprompt ： 如果你想直接跟GPT一条一条的对话，需要在开始时适用GPTs上的开始语，并在结束时使用结束提示语 #GPT提示语 \n/removelast 删除最后一条信息。（注意：直接编辑信息并不会修改错误的记录！）\n/today 发送今天的日期。\n/nowstart 把当前时间作为开始时间。（描述为：XX时间开始）\n/nowend 把当前时间作为结束时间。（描述为：直到XX时间结束）") 
                        send_message(chat_id_str, f"#ChatGPT————日记助手GPTs：https://chat.openai.com/g/g-mj9dk2h4X-ri-ji-zhu-shou")
                        send_message(chat_id_str, f"#ChatGPT————日程助手GPTs：https://chat.openai.com/g/g-ieyhqf6J9-ri-cheng-zhu-shou")          
                        blacklist.append(unique_id)
                    # elif message_text.lower() == "/prompt":
                    #     current_date = datetime.now().strftime("%Y年%m月%d日")
                    #     send_message(chat_id_str, f"#GPT提示词\n---\n```\nDear ChatGPT, 今天是{current_date}. 我希望你能成为我的日记助手。请注意: 在这一天里，无论我输入什么内容，你都只需要回复: \"####\" . 只有当我输入\"Hi ChatGPT, 让我们结束今天的日记\"时，你才开始执行我规定的任务.\n```")   
                    #     blacklist.append(unique_id)
                    elif message_text.lower() == "/stopprompt":
                        send_message(chat_id_str, "#GPT提示词\n---\n```\nHi ChatGPT, 让我们结束今天的记录\n```")   
                        blacklist.append(unique_id)
                    elif message_text.lower() == "/done":
                        send_message(chat_id_str, f"#二次确认\n---\n你真的要结束本次记录吗？确认请点击： /confirmdone \n如果不想结束本次记录，直接忽视这条信息、继续发送信息或使用其他指令都可以。")                        
                        blacklist.append(unique_id)
                    elif message_text.lower() == "/confirmdone":
                        main_text="\n\n".join(user_data.get(chat_id_str, []))
                        send_message(chat_id_str, f"#结束记录\n以下是记录的全部内容：")
                        send_message(chat_id_str, f"\n---\n```\n{main_text}\n```\n---\n")
                        send_message(chat_id_str, f"下次发送消息将开始新的记录.")
                        user_data[chat_id_str] = []
                        blacklist.append(unique_id)
                    elif message_text.lower() == "/check":
                        print(f"user_data: {user_data}")
                        main_text="\n\n".join(user_data.get(chat_id_str, []))
                        send_message(chat_id_str, f"#查看记录\n以下是已记录的全部内容：\n---\n```\n{main_text}\n```\n---\n发送消息将继续当前的记录.")
                        blacklist.append(unique_id)
                    elif message_text.lower() == "/removelast":
                        if user_data[chat_id_str]:
                            user_data[chat_id_str].pop()          
                            send_message(chat_id, f"#操作提醒\n---\n最后一条信息已成功删除。")                  
                        else:
                            send_message(chat_id, "#操作提醒\n---\n没有消息可以删除。")
                        blacklist.append(unique_id)
                    elif message_text.lower() == "/today":
                        today_date = datetime.now().strftime("%Y年%m月%d日")
                        send_message(chat_id_str, f"#记录成功\n---\n```\n{today_date}\n```\n---\n【信息记录时间：{current_datetime}】")                        
                        if chat_id_str not in user_data:
                            user_data[chat_id_str] = []
                        user_data[chat_id_str].append(today_date)
                        blacklist.append(unique_id)
                    elif message_text.lower() == "/nowstart":
                        current_time = datetime.now().strftime("%H:%M开始")
                        send_message(chat_id_str, f"#记录成功\n---\n```\n{current_time}\n```\n---\n【信息记录时间：{current_datetime}】")                        
                        if chat_id_str not in user_data:
                            user_data[chat_id_str] = []
                        user_data[chat_id_str].append(current_time)
                        blacklist.append(unique_id)
                    elif message_text.lower() == "/nowend":
                        current_time = datetime.now().strftime("直到%H:%M结束")
                        send_message(chat_id_str, f"#记录成功\n---\n```\n{current_time}\n```\n---\n【信息记录时间：{current_datetime}】")                        
                        if chat_id_str not in user_data:
                            user_data[chat_id_str] = []
                        user_data[chat_id_str].append(current_time)
                        blacklist.append(unique_id)
                    else:
                        send_message(chat_id_str, f"{message_text_with_datetime}")
                        if chat_id_str not in user_data:
                            user_data[chat_id_str] = []
                        user_data[chat_id_str].append(message_text)
                        blacklist.append(unique_id)  

                        

                    # 保存数据到文件
                    with open(os.path.join(current_dir, user_data_filename), 'w') as f:
                        json.dump(user_data, f)
                    with open(os.path.join(current_dir, blacklist_filename), 'w') as f:
                        json.dump(blacklist, f)

                
                # 保存数据到文件
                with open(os.path.join(current_dir, user_data_filename), 'w') as f:
                    json.dump(user_data, f)
                with open(os.path.join(current_dir, blacklist_filename), 'w') as f:
                    json.dump(blacklist, f)

            
                              
        else:
            print(f"{URL} Received updates: {updates}")
            print("Error or no updates; retrying in 10 seconds...")
            time.sleep(10) 
        

        print("Process message queue...")
        process_message_queue()
        

# 运行主函数
if __name__ == '__main__':
    main()




