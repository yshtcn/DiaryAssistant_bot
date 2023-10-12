# 使用官方的 Python 3.11 镜像作为基础镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /usr/src/app

# 将当前目录下的所有文件复制到镜像中的工作目录
COPY DiaryAssistant.py ./


# 创建/data目录用于存储生成的文件并设置777权限
RUN mkdir /data && chmod -R 777 /data

# 定义环境变量 PIP_INDEX_URL 并设置其默认值为清华大学的更新源
ENV PIP_INDEX_URL=https://pypi.tuna.tsinghua.edu.cn/simple

# 安装 Python 依赖
RUN pip install --no-cache-dir -i $PIP_INDEX_URL requests

# 设置容器启动后执行的命令
CMD [ "python", "./Diary Assistant.py" ]
