def 刪除指定名稱快取(快取, 名稱):
    c, n = 快取, 名稱
    keys_to_delete = [key for key in c if isinstance(key, tuple) and key[0] == n]
    for key in keys_to_delete:
        c.delete(key)
