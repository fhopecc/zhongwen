from pathlib import Path
import logging
logger = logging.getLogger(Path(__file__).stem)

if __name__ == '__main__':
    '同步小狼毫輸入法設定檔至雲端硬碟'
    from zhongwen.檔 import 同步目錄
    from pathlib import Path
    import time
    import os
    rime_dir = Path(os.environ['AppData']) / 'Rime'
    backup_rime_dir = Path(r'G:\我的雲端硬碟\小狼毫輸入法') 
    同步目錄(str(backup_rime_dir), str(rime_dir)) 
    logger.info(f'初始同步{backup_rime_dir}至{rime_dir}')
    while True:
        同步目錄(str(rime_dir), str(backup_rime_dir)) 
        logger.info(f'同步{rime_dir}至{backup_rime_dir}')
        time.sleep(300)
