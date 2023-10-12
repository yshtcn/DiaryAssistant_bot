# Set-ExecutionPolicy RemoteSigned -Scope CurrentUser

# 检查是否以管理员权限运行
if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    # 请求管理员权限
    Start-Process powershell -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
    exit
}

# 更改到脚本的目录
Set-Location $PSScriptRoot


# 获取当前日期和时间
$dateTime = Get-Date -Format "yyyyMMdd"

# 输出提示并获取版本的最后一位
$revision = Read-Host -Prompt "请输入今天的版本次 ($dateTime,[?])"

# 构建版本号
$version = "$dateTime" + "_$revision"

# 构建并打上版本号标签的 Docker 镜像
docker build -t yshtcn/diary-assistant:$version .

# 推送具有版本号标签的 Docker 镜像到 Docker Hub
docker push yshtcn/diary-assistant:$version

# 为镜像打上 'latest' 标签并推送
docker tag yshtcn/diary-assistant:$version yshtcn/diary-assistant:Test
docker push yshtcn/diary-assistant:Test

pause