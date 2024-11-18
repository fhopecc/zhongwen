from diskcache import Cache
from pathlib import Path

cache = Cache(Path.home() / 'cache' / Path(__file__).stem)

@cache.memoize('讀取審計部公有土地清冊')
def 讀取審計部公有土地清冊(檔案路徑字串):
    import pandas as pd
    publand_file = Path(檔案路徑字串)
    df = pd.read_csv(publand_file)
    df['12碼地段號'] = df['12碼地段號'].map(lambda n: f"{int(n):012d}")
    return df
