import configparser
import os

# 設定をキャッシュするための変数
_config = None

def get_config():
    global _config
    if _config is None:
        # config.ini のパスを取得
        config_path = os.path.join(os.path.dirname(__file__), 'parameter.ini')

        # configparserで読み込み
        _config = configparser.ConfigParser()
        _config.read(config_path)

    return _config
