# config.template.py
# 設定テンプレートファイル - このファイルをconfig.pyにコピーして使用してください

CONFIG = {
    # 使用するプロバイダー ("pixabay" または "pexels")
    "provider": "pixabay",
    
    # 検索キーワード
    "query": "cats",
    
    # ダウンロードする画像数
    "n": 20,
    
    # 最小画像サイズ (Pixabayのみ、Noneで制限なし)
    "min_width": 1024,
    "min_height": 768,
    
    # リクエスト間の待機時間（秒）
    "delay": 0.3
}