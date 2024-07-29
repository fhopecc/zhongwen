'windows 系統管理工具'
from pathlib import Path
import os
import logging
logger = logging.getLogger(Path(__file__).stem)

def setx(var, value):
    '設定 Windows 環境變數'
    #cmd = f'setx {var} {value} /M >nul 2>nul'
    cmd = f'setx {var} "{value}"'
    if not (r:=os.system(cmd)) == 0:
        raise WindowsError(f'設定 Windows 環境變數指令[{cmd}]失敗，回傳值為[{r}]！')
    print(f'設定 Windows 環境變數[{var}]為[{value}]成功！')

def addpath(p, path_var='PATH'):
    p = str(p)
    ps = os.environ[path_var].split(';')
    if p not in ps:
        p = p.replace('"', '')
        ps.append(p)
        ps = list(set(ps))
        setx(path_var, ';'.join(ps))

TEMP = Path(os.environ['TEMP'])

def downloads():
    return Path.home() / 'Downloads'

def services():
    resume = 0
    accessSCM = win32con.GENERIC_READ
    accessSrv = win32service.SC_MANAGER_ALL_ACCESS

    #Open Service Control Manager
    hscm = win32service.OpenSCManager(None, None, accessSCM)

    #Enumerate Service Control Manager DB
    typeFilter = win32service.SERVICE_WIN32
    stateFilter = win32service.SERVICE_STATE_ALL

    statuses = win32service.EnumServicesStatus(hscm, typeFilter, stateFilter)

    return [short_name for (short_name, desc, status) in statuses]

def 是否安裝(software):
    from windows_tools.installed_software import get_installed_software
    for s in [s['name'] for s in get_installed_software()]:
        if software in s:
            return True
    return False

def powershell(cmd):
    import subprocess
    result = subprocess.run(["powershell", "-Command", cmd], capture_output=True)
    if result.returncode !=0:
        raise WindowsError(f'執行 powershell 發生錯誤：{result}；指令{cmd}')

def remove_cortan():
    cmd = 'Get-AppxPackage -allusers Microsoft.549981C3F5F10 | Remove-AppxPackage'        
    powershell(cmd)    

def 建立傳送到項目(名稱:str, 命令:str):
    import os
    import winshell
    批次檔 = Path(winshell.sendto()) / f"{名稱}.bat"
    批次檔.write_text(命令)
    logger.info(f'建立傳送到【{名稱}】。')

def 增加所有檔案右鍵選單之功能(功能名稱:str, 指令:str):
    import winreg as reg
    import os
    import sys

    # 功能名稱
    context_menu_name = 功能名稱
    
    key_path = fr'*\shell\{context_menu_name}'
    command_key_path = fr'*\shell\{context_menu_name}\command'

    # 創建註冊表項目
    try:
        reg.CreateKey(reg.HKEY_CLASSES_ROOT, key_path)
        reg.CreateKey(reg.HKEY_CLASSES_ROOT, command_key_path)
        
        # 設置右鍵選單項目名稱
        with reg.OpenKey(reg.HKEY_CLASSES_ROOT, key_path, 0, reg.KEY_WRITE) as key:
            reg.SetValue(key, '', reg.REG_SZ, context_menu_name)

        # 設置指令
        with reg.OpenKey(reg.HKEY_CLASSES_ROOT, command_key_path, 0, reg.KEY_WRITE) as key:
            reg.SetValue(key, '', reg.REG_SZ, 指令)
        print(f"所有檔案右鍵選單增加【{功能名稱}】項目。")
    except Exception as e:
        print(f"添加右鍵選單項目時出錯: {e}")

def where(command):
    '查找指定的可執行檔，以Windows where.exe 實作。'
    import subprocess
    result = subprocess.run(['where', command], capture_output=True, text=True)
    paths = result.stdout.strip().split('\n')
    return paths
