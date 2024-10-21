def 修正英特爾網卡無線網路下載速度緩慢問題():
    '參考：https://www.reddit.com/r/HomeNetworking/comments/14slwlo/slow_wifi_speeds_with_ax211_intel_wifi_card/'
    import os
    # cmd = 'netsh interface set interface "Wi-Fi" admin=disable'
    # os.system(cmd)
    # cmd = 'netsh interface set interface "Wi-Fi" admin=enable'
    # os.system(cmd)
    cmd = 'netsh int tcp set global autotuninglevel=normal'
    os.system(cmd)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-w", "--fix_intel_wifi_slow"
                       ,help="修正英特爾網卡無線網路下載速度緩慢問題"
                       ,action="store_true")
    args = parser.parse_args()
    if args.fix_intel_wifi_slow:
        修正英特爾網卡無線網路下載速度緩慢問題()
