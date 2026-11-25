'windows 系統管理工具'
from pathlib import Path
import logging
import os

logger = logging.getLogger(Path(__file__).stem)

def setx(var, value):
    '設定 Windows 環境變數'
    #cmd = f'setx {var} {value} /M >nul 2>nul'
    cmd = f'setx {var} "{value}"'
    if not (r:=os.system(cmd)) == 0:
        raise WindowsError(f'設定 Windows 環境變數指令[{cmd}]失敗，回傳值為[{r}]！')
    cmd = f'set {var}="{value}"'
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

def 增加檔案右鍵選單功能(功能名稱: str, 指令: str, 副檔名: str = '*') -> bool:
    '''
    一、在目前使用者（HKCU）登錄檔註冊檔案右鍵選單項目，不需系統管理員權限。
    二、副檔名參數：
        '*'                     : 所有檔案
        'pdf' 或 '.pdf'         : 該副檔名，寫入 SystemFileAssociations，不受預設開啟程式影響
        'FoxitReader.Document'  : 指定 ProgID，僅在該程式為預設開啟程式時有效
    三、由 opus5.5 修正。
    '''
    import winreg as reg

    if 副檔名 == '*':
        根路徑 = '*'
    elif 副檔名.startswith('.') or '.' not in 副檔名:
        根路徑 = rf'SystemFileAssociations\.{副檔名.lstrip(".")}'
    else:
        根路徑 = 副檔名  # 視為 ProgID

    key_path = rf'Software\Classes\{根路徑}\shell\{功能名稱}'
    command_key_path = key_path + r'\command'

    try:
        with reg.CreateKeyEx(reg.HKEY_CURRENT_USER, key_path, 0, reg.KEY_WRITE) as key:
            reg.SetValueEx(key, '', 0, reg.REG_SZ, 功能名稱)
        with reg.CreateKeyEx(reg.HKEY_CURRENT_USER, command_key_path, 0, reg.KEY_WRITE) as key:
            reg.SetValueEx(key, '', 0, reg.REG_SZ, 指令)
    except OSError as e:
        logger.error(f'添加右鍵選單項目【{功能名稱}】時出錯（HKCU\\{key_path}）：{e}')
        return False

    if 副檔名 == '*':
        logger.info(f'所有檔案右鍵選單增加【{功能名稱}】項目。')
    else:
        logger.info(f'{副檔名} 右鍵選單增加【{功能名稱}】項目（HKCU\\{key_path}）。')
    return True

def where(command):
    '查找指定的可執行檔，以Windows where.exe 實作。'
    import subprocess
    result = subprocess.run(['where', command], capture_output=True, text=True)
    paths = result.stdout.strip().split('\n')
    return paths

def 設定預設右鍵選單():
    import sys
    cmd = f'"{sys.executable}" -m zhongwen.file --copytext "%1"' 
    增加檔案右鍵選單功能('複製檔案文字', cmd, '*')
    cmd = f'"{sys.executable}" -m zhongwen.file --file2text "%1"' 
    增加檔案右鍵選單功能('轉文字檔', cmd, '*')
