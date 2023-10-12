@echo off


title "AutoPyInstaller：安装升级pyinstaller"
:: 安装/更新pyinstaller(注意：不希望自动安装/更新pyinstaller记得注释掉）
pip install pyinstaller -i https://pypi.tuna.tsinghua.edu.cn/simple

title "AutoPyInstaller：安装升级程序所用到的库"
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
cls

:: 更新标题
title "AutoPyInstaller：初始化"

:: 让我们设置一些信息
set "ProductName=Diary Assistant"
set "InternalName=yshtcn"
set "Comments=GitHub: https://github.com/yshtcn/DiaryAssistant_bot"


:: 进入批处理所在的目录
cd /d %~dp0



:: 更新标题
title "AutoPyInstaller：生成版本文件"



:: 使用WMIC获取当前日期
for /f "delims=" %%a in ('wmic os get localdatetime ^| find "."') do set datetime=%%a


:: 分解日期时间字符串
set "year=%datetime:~0,4%"
set "month=%datetime:~4,2%"
set "day=%datetime:~6,2%"

:: 获取版本的最后一位
set /p "revision=请输入今天的版本次:(%year%, %month%, %day%,[?]):"

:: 当前版本目录（未去除先导0）
set "versionFolder=%year%_%month%_%day%_%revision%"

:: 去除月和日的前导零（如果有）
set /a "month=1%month%-100"
set /a "day=1%day%-100"

:: 初始化临时文件
set "tempFile=temp.txt"

:: 清空或创建临时文件
echo. > %tempFile%

:: 逐行写入临时文件
echo # version_info.txt >> %tempFile%
echo VSVersionInfo( >> %tempFile%
echo   ffi=FixedFileInfo( >> %tempFile%
echo     filevers=(%year%, %month%, %day%, %revision%), >> %tempFile%
echo     prodvers=(%year%, %month%, %day%, %revision%), >> %tempFile%
echo     mask=0x3f, >> %tempFile%
echo     flags=0x0, >> %tempFile%
echo     OS=0x4, >> %tempFile%
echo     fileType=0x1, >> %tempFile%
echo     subtype=0x0, >> %tempFile%
echo     date=(0, 0) >> %tempFile%
echo   ), >> %tempFile%
echo   kids=[ >> %tempFile%
echo     StringFileInfo( >> %tempFile%
echo       [ >> %tempFile%
echo       StringTable( >> %tempFile%
echo         '040904B0', >> %tempFile%
echo         [StringStruct('ProductName', '%ProductName%'), >> %tempFile%
echo         StringStruct('ProductVersion', '%year%, %month%, %day%, %revision%'), >> %tempFile%
echo         StringStruct('InternalName', '%InternalName%'), >> %tempFile%
echo         StringStruct('CompanyName', 'ysht.me - %Comments%'), >> %tempFile%
echo         StringStruct('Comments', '%Comments%'), >> %tempFile%
echo         StringStruct('LegalCopyright', 'Apache-2.0 license - %Comments%'), >> %tempFile%
echo         ] >> %tempFile%
echo       ), >> %tempFile%
echo       ] >> %tempFile%
echo     ), >> %tempFile%
echo     VarFileInfo([VarStruct('Translation', [0x804, 1200])]) >> %tempFile%
echo   ] >> %tempFile%
echo ) >> %tempFile%

:: 将临时文件内容移动到最终的 version_info.txt
move /Y %tempFile% version_info.txt

:: 输出完成信息
echo 版本信息已成功生成。

::更新标题
title "AutoPyInstaller：开始打包"

:: 创建打包目录（如果不存在）
md build
:: 删除打包目录下同版本号的文件夹
rd /S /Q %~dp0\build\%versionFolder%

:: 删除打包目录产生的过程文件
del /q %~dp0\build\heartbeat.spec
rd /S /Q %~dp0\build\build

:: 进入打包目录并开始打包
cd /d %~dp0\build
pyinstaller --onefile --version-file %~dp0\version_info.txt "%~dp0\Diary Assistant.py"

::更新标题
title "AutoPyInstaller：打包完毕，进行一些收尾工作"
:: （再次）删除打包目录下同版本号的文件夹
rd /S /Q %~dp0\build\%versionFolder%
:: （再次）删除打包目录产生的过程文件
del /q "%~dp0\build\Diary Assistant.spec"
rd /S /Q %~dp0\build\build

:: 把生成打包的目录以版本号重命名
rename dist %versionFolder%

:: 添加需要一起打包的文件
copy %~dp0\config.Exsample.ini %~dp0\build\%versionFolder%\
copy %~dp0\README.md %~dp0\build\%versionFolder%\