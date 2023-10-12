# DiaryAssistant_bot

## 这是一个收集信息的Telegram bot，它的作用很简单：

- 用户向它发送消息，它会回复用户消息已记录。
- 使用完成或者查看指令，会把之前用户发送的信息合并成一条信息，发送给用户。
- 当使用完成指令时，它会在发送合并信息之后，清空之前保存的信息，方便用户开始新的记录。

## 为什么要制作这个bot？

原因很简单，因为AI日记的兴起————我们可以把AI当成朋友一样不断的诉说，最后让AI回顾整理一天的事情成为日记。最初我是使用chatGPT完成这一点的，但是始终在AI的界面进行对话十分不便，而且GPT的对话次数是有限的，有时候太碎碎念会造成对话次数受限。于是我设计、开发了这个bot。

## 为什么要开源发布而不是直接提供bot？

首先日记这个东西很私密，你不知道bot或者其他软件的另一端有谁在盯着，我建议还是在自己的电脑/服务器上跑好一点。

# 使用方法

## Windows版本

- [在Release下载最新版本](https://github.com/yshtcn/DiaryAssistant_bot/releases)。
- 首次运行时，会自动生成bot_config.json，并自动提示按任意键退出。
- 然后把你的botid填进bot_config.json，并配置好代理地址（如果不需要代理地址，直接删除代理信息即可）。
- 再次启动，向你的bot发送/start看看是否可以正常运行就可以了。

## Docker版本

```docker run -v /mydata:/data yshtcn/diary-assistant:latest```

把/mydata换成映射的目的路径，首次运行时，会自动生成bot_config.json，并自动退出。
然后把你的botid填进映射目的地址下的bot_config.json，并配置好代理地址（如果不需要代理地址，直接删除代理信息即可）。
再次启动，向你的bot发送/start看看是否可以正常运行就可以了。
