def 提出請求(請求事項:str):
    import os
    r = 請求事項
    if '法規' in r:
        r = r.replace('法規', '')
        cmd = f'start https://glrslaw.e-land.gov.tw/SearchAllResultList.aspx?KW={r}'
        os.system(cmd)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-q", "--query", help="提出請求")
    args = parser.parse_args()
    if args.query:
        提出請求(args.query)
