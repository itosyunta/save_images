# Image Downloader

PixabayとPexels APIを使用して画像を自動ダウンロードするPythonスクリプトです。

## 特徴

- 🔍 **複数のAPI対応**: PixabayとPexelsの両方に対応
- 📁 **自動フォルダ作成**: 検索キーワードごとにフォルダを自動作成
- 🔒 **安全な設定管理**: 環境変数でAPIキーを管理
- ⚡ **レート制限対応**: API制限情報の表示と適切な待機
- 🎯 **重複回避**: 同じ画像の重複ダウンロードを防止
- 📊 **詳細なログ**: ダウンロード進捗と結果の表示
- 🧹 **自動クリーンアップ**: 検索結果がない場合の空フォルダ削除

## インストール

### 1. リポジトリのクローン
```bash
git clone https://github.com/your-username/image-downloader.git
cd image-downloader
```

### 2. 仮想環境の作成（推奨）
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# または
venv\\Scripts\\activate   # Windows
```

### 3. 依存関係のインストール
```bash
pip install -r requirements.txt
```

### 4. 設定ファイルの作成
設定テンプレートをコピーして個人用設定ファイルを作成：
```bash
cp config.template.py config.py  # Linux/Mac
# または
copy config.template.py config.py  # Windows
```

### 5. 環境変数の設定
`.env.template`をコピーして`.env`ファイルを作成：
```bash
cp .env.template .env
```

`.env`ファイルを編集してAPIキーを設定：
```env
# Pixabay API Key (https://pixabay.com/api/docs/)
PIXABAY_API_KEY=your_pixabay_api_key_here

# Pexels API Key (https://www.pexels.com/api/)
PEXELS_API_KEY=your_pexels_api_key_here
```

## APIキーの取得

### Pixabay
1. [Pixabay](https://pixabay.com/)でアカウント作成
2. [API documentation](https://pixabay.com/api/docs/)ページでAPIキーを取得

### Pexels
1. [Pexels](https://www.pexels.com/)でアカウント作成
2. [API](https://www.pexels.com/api/)ページでAPIキーを取得

## 使用方法

### 1. 設定の変更
`config.py`ファイルの`CONFIG`辞書を編集：

```python
CONFIG = {
    "provider": "pixabay",     # "pixabay" または "pexels"
    "query": "cats",           # 検索キーワード
    "save_folder": "./downloads",  # 保存先フォルダ（クエリごとにサブフォルダ作成）
    "n": 20,                   # ダウンロード枚数
    "min_width": 1024,         # 最小幅（Pixabayのみ）
    "min_height": 768,         # 最小高さ（Pixabayのみ）
    "delay": 0.3               # リクエスト間隔（秒）
}
```

### 2. スクリプトの実行
```bash
python save_samples.py
```

## 出力例

```
プロバイダー: pixabay
検索キーワード: cats
保存先: ./downloads/cats
既存ファイル数: 0
目標ファイル数: 20
追加ダウンロード予定: 20 個
最小サイズ: 1024x768
ダウンロード開始...

📊 API制限情報:
   制限数: 100/60秒
   残り: 95リクエスト
   リセットまで: 45秒

🔍 検索結果:
   総件数: 24,567 件
   利用可能: 500 件
✅ 検索成功！

[1] ./downloads/cats/a1b2c3d4e5f6g7h8.jpg
[2] ./downloads/cats/i9j0k1l2m3n4o5p6.jpg
...
[20] ./downloads/cats/x9y8z7w6v5u4t3s2.jpg

✅ 完了: 20 個の新しいファイルを追加しました
📁 総ファイル数: 20 個 (./downloads/cats)
```

## ファイル構造

```
image-downloader/
├── save_samples.py      # メインスクリプト
├── config.py            # 個人設定（Gitで管理されません）
├── config.template.py   # 設定テンプレート
├── .env                 # 環境変数（Gitで管理されません）
├── .env.template        # 環境変数のテンプレート
├── requirements.txt     # 必要なPythonパッケージ
├── .gitignore          # Git除外ファイル
├── README.md           # このファイル
├── LICENSE             # ライセンス
└── downloads/          # ダウンロードした画像（Gitで管理されません）
    ├── cats/
    ├── dogs/
    └── ...
```

## 設定項目

| 項目 | 説明 | デフォルト |
|------|------|------------|
| `provider` | 使用するAPI ("pixabay" または "pexels") | "pixabay" |
| `query` | 検索キーワード | "cats" |
| `n` | ダウンロード枚数 | 20 |
| `min_width` | 最小画像幅（Pixabayのみ） | 1024 |
| `min_height` | 最小画像高さ（Pixabayのみ） | 768 |
| `delay` | リクエスト間隔（秒） | 0.3 |

## 注意事項

- 各APIには利用制限があります（Pixabay: 100回/分、Pexels: 200回/時）
- 商用利用の場合は各サービスの利用規約を確認してください
- 大量のダウンロードは控えめに行ってください

## トラブルシューティング

### 設定ファイルエラー
```
❌ エラー: config.py ファイルが見つかりません
```
→ `config.template.py`を`config.py`にコピーしてから実行してください

### APIキーエラー
```
エラー: PIXABAY_API_KEY が .env ファイルに設定されていません
```
→ `.env`ファイルでAPIキーが正しく設定されているか確認してください

### 検索結果なし
```
❌ キーワード 'xyz123' の検索結果が見つかりませんでした。
```
→ 英語のキーワードを試すか、より一般的な単語を使用してください

### ネットワークエラー
```
❌ API リクエストエラー: Connection timeout
```
→ インターネット接続を確認してください

## ライセンス

MIT License - 詳細は[LICENSE](LICENSE)ファイルを参照してください。

## 貢献

プルリクエストやイシューは歓迎します！

## 更新履歴

- v1.0.0: 初回リリース
  - Pixabay/Pexels API対応
  - 自動フォルダ作成
  - レート制限表示
  - エラーハンドリング