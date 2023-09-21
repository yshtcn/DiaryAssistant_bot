# 修改代码以记录黑名单而非删除消息

# 示例代码（请在本地环境中运行）
import json
import requests
import time
from datetime import datetime

# 配置代理
proxies = {
    'http': 'http://127.0.0.1:7890',
    'https': 'http://127.0.0.1:7890'
}

# Bot Token
TOKEN = "demo"
URL = f"https://api.telegram.org/bot{TOKEN}/"

# 尝试从文件中加载已有数据
try:
    with open('user_data.json', 'r') as f:
        user_data = json.load(f)
except FileNotFoundError:
    user_data = {}

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
        url = URL + "sendMessage"
        params = {'chat_id': chat_id, 'text': text}
        r = requests.get(url, params=params, proxies=proxies)
    except Exception as e:
        print(f"Error sending message: {e}")

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
                unique_id = f"{chat_id}_{message_id}"
                
                # 初始化用户数据
                if chat_id not in user_data:
                    user_data[chat_id] = []
                
                # 检查黑名单
                if unique_id not in blacklist:
                    # 处理“done”命令
                    if message_text.lower() == "todaydone":
                        send_message(chat_id, "\n".join(user_data[chat_id]))
                        user_data[chat_id] = []
                    else:
                        send_message(chat_id, f"{message_text_with_datetime}")
                        user_data[chat_id].append(message_text)
                        blacklist.append(unique_id)  # 添加到黑名单
                
                # 保存数据到文件
                with open('user_data.json', 'w') as f:
                    json.dump(user_data, f)
                with open('blacklist.json', 'w') as f:
                    json.dump(blacklist, f)
        else:
            print("Error or no updates; retrying in 5 seconds...")
            time.sleep(5)  # 等待5秒再重试

        # 每1分钟检查一次
        time.sleep(30)

# 运行主函数
if __name__ == '__main__':
    main()




