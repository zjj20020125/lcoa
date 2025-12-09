@echo off
chcp 65001 >nul

REM 设置日志文件路径（使用绝对路径）
set LOG_DIR=D:\desktop\源码\server\logs
set LOG_FILE=%LOG_DIR%\scheduled_task_manual.log

REM 创建logs目录（如果不存在）
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"

REM 写入开始日志
echo [%date% %time%] 开始执行定时任务 > "%LOG_FILE%"
echo 正在运行数据处理脚本... >> "%LOG_FILE%"

REM 切换到项目根目录
cd /d "D:\desktop\源码\server"

REM 记录当前目录和Python信息
echo 执行目录: %CD% >> "%LOG_FILE%"
echo Python路径信息: >> "%LOG_FILE%"
C:\Windows\py.exe -3 --version >> "%LOG_FILE%" 2>&1
echo. >> "%LOG_FILE%"

REM 使用Python执行脚本
C:\Windows\py.exe -3 "D:\desktop\源码\server\lcoa\datedeal\run_scheduled.py" >> "%LOG_FILE%" 2>&1

if %ERRORLEVEL% EQU 0 (
    echo [%date% %time%] 脚本执行成功 >> "%LOG_FILE%"
) else (
    echo [%date% %time%] 脚本执行失败，错误代码: %ERRORLEVEL% >> "%LOG_FILE%"
)