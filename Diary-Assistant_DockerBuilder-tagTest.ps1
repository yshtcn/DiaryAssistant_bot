# Set-ExecutionPolicy RemoteSigned -Scope CurrentUser

# ����Ƿ��Թ���ԱȨ������
if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    # �������ԱȨ��
    Start-Process powershell -ArgumentList "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`"" -Verb RunAs
    exit
}

# ���ĵ��ű���Ŀ¼
Set-Location $PSScriptRoot


# ��ȡ��ǰ���ں�ʱ��
$dateTime = Get-Date -Format "yyyyMMdd"

# �����ʾ����ȡ�汾�����һλ
$revision = Read-Host -Prompt "���������İ汾�� ($dateTime,[?])"

# �����汾��
$version = "$dateTime" + "_$revision"

# ���������ϰ汾�ű�ǩ�� Docker ����
docker build -t yshtcn/diary-assistant:$version .

# ���;��а汾�ű�ǩ�� Docker ���� Docker Hub
docker push yshtcn/diary-assistant:$version

# Ϊ������� 'latest' ��ǩ������
docker tag yshtcn/diary-assistant:$version yshtcn/diary-assistant:Test
docker push yshtcn/diary-assistant:Test

pause