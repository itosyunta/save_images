# save_samples.py
# 画像ダウンロードスクリプト

import hashlib
import os
import sys
import time
from pathlib import Path

import requests
from dotenv import load_dotenv

# 設定ファイルを読み込み
try:
    from config import CONFIG
except ImportError:
    print("❌ エラー: config.py ファイルが見つかりません")
    print("config.template.py を config.py にコピーしてから実行してください:")
    print("  copy config.template.py config.py")
    sys.exit(1)

# .envファイルから環境変数を読み込み
load_dotenv()

def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def ensure_dir(p):
    Path(p).mkdir(parents=True, exist_ok=True)

def cleanup_empty_folder(folder_path, was_newly_created):
    """空のフォルダを削除する（新規作成された場合のみ）"""
    if not was_newly_created:
        return False
    
    try:
        folder = Path(folder_path)
        if folder.exists() and folder.is_dir():
            # フォルダ内のファイルをチェック
            files = list(folder.glob("*"))
            if not files:  # 空の場合
                folder.rmdir()
                print(f"🗑️  空のフォルダを削除しました: {folder}")
                return True
    except Exception as e:
        print(f"⚠️  フォルダ削除に失敗: {e}", file=sys.stderr)
    return False


def sanitize_folder_name(name):
    """フォルダ名として使用できない文字を置換する"""
    # Windowsで使用できない文字を置換
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        name = name.replace(char, '_')
    # 連続するスペースをアンダースコアに置換
    name = '_'.join(name.split())
    # 先頭・末尾の不要な文字を削除
    name = name.strip('._')
    return name if name else 'unknown'


def download(url, outdir):
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    ext = ".jpg"
    h = sha256_bytes(r.content)[:16]
    fp = Path(outdir) / f"{h}{ext}"
    if not fp.exists():
        with open(fp, "wb") as f:
            f.write(r.content)
    return str(fp)

def search_pixabay(api_key, query, per_page, page, min_w=None, min_h=None):
    params = {
        "key": api_key, 
        "q": query, 
        "image_type": "photo",
        "safesearch": "true", 
        "per_page": per_page, 
        "page": page,
    }
    if min_w:
        params["min_width"] = min_w
    if min_h:
        params["min_height"] = min_h
    
    url = "https://pixabay.com/api/"
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    data = r.json()
    
    # レート制限情報を取得
    rate_limit_info = {
        'limit': r.headers.get('X-RateLimit-Limit'),
        'remaining': r.headers.get('X-RateLimit-Remaining'),
        'reset': r.headers.get('X-RateLimit-Reset')
    }
    
    # 検索結果情報を取得
    search_info = {
        'total': data.get('total', 0),
        'totalHits': data.get('totalHits', 0),
        'current_page': page,
        'per_page': per_page
    }
    
    # 画像URL: largeImageURL or webformatURL
    urls = [
        hit.get("largeImageURL") or hit.get("webformatURL") 
        for hit in data.get("hits", []) 
        if hit.get("largeImageURL") or hit.get("webformatURL")
    ]
    return urls, rate_limit_info, search_info

def search_pexels(api_key, query, per_page, page):
    headers = {"Authorization": api_key}
    params = {"query": query, "per_page": per_page, "page": page}
    url = "https://api.pexels.com/v1/search"
    r = requests.get(url, headers=headers, params=params, timeout=30)
    r.raise_for_status()
    data = r.json()
    
    # 検索結果情報を取得
    search_info = {
        'total': data.get('total_results', 0),
        'totalHits': data.get('total_results', 0),  # Pexelsは同じ値
        'current_page': page,
        'per_page': per_page
    }
    
    # 画像URL候補: original (最大), large, large2x, etc.
    urls = []
    for p in data.get("photos", []):
        src = p.get("src", {})
        url_candidate = (
            src.get("original") or 
            src.get("large2x") or 
            src.get("large") or 
            src.get("medium")
        )
        urls.append(url_candidate)
    urls = [u for u in urls if u]
    return urls, search_info

def display_rate_limit_info(rate_info):
    """レート制限情報を表示する"""
    if any(rate_info.values()):
        print("📊 API制限情報:")
        if rate_info['limit']:
            print(f"   制限数: {rate_info['limit']}/60秒")
        if rate_info['remaining']:
            print(f"   残り: {rate_info['remaining']}リクエスト")
        if rate_info['reset']:
            print(f"   リセットまで: {rate_info['reset']}秒")
        print()


def display_search_info(search_info, provider, folder_path=None, 
                       was_newly_created=False):
    """検索結果情報を表示する"""
    total = search_info.get('total', 0)
    totalHits = search_info.get('totalHits', 0)
    
    print("🔍 検索結果:")
    print(f"   総件数: {total:,} 件")
    print(f"   利用可能: {totalHits:,} 件")
    
    if total == 0:
        print(f"❌ キーワード '{CONFIG['query']}' の検索結果が見つかりませんでした。")
        print("   💡 検索のヒント:")
        print("      - 英語のキーワードを試してください")
        print("      - より一般的な単語を使用してください") 
        print("      - スペルを確認してください")
        if (provider == "pixabay" and 
            (CONFIG.get('min_width') or CONFIG.get('min_height'))):
            print("      - 最小サイズ制限を緩和してください")
        
        # 新規作成されたフォルダがある場合は削除
        if folder_path and was_newly_created:
            cleanup_empty_folder(folder_path, was_newly_created)
        
        return False
    elif totalHits == 0:
        print("❌ 検索結果は見つかりましたが、利用可能な画像がありません。")
        
        # 新規作成されたフォルダがある場合は削除
        if folder_path and was_newly_created:
            cleanup_empty_folder(folder_path, was_newly_created)
            
        return False
    else:
        print("✅ 検索成功！")
        return True

def main():
    # 設定を読み込み
    provider = CONFIG["provider"]
    query = CONFIG["query"]
    n = CONFIG["n"]
    min_width = CONFIG["min_width"]
    min_height = CONFIG["min_height"]
    delay = CONFIG["delay"]
    
    # .envファイルから保存先フォルダを取得
    base_folder = os.getenv("SAVE_FOLDER", "./samples")
    
    # クエリ用のサブフォルダを作成
    query_folder = sanitize_folder_name(query)
    out = Path(base_folder) / query_folder
    
    # .envファイルからAPIキーを取得
    if provider == "pixabay":
        api_key = os.getenv("PIXABAY_API_KEY")
    elif provider == "pexels":
        api_key = os.getenv("PEXELS_API_KEY")
    else:
        print(f"エラー: 対応していないプロバイダーです: {provider}")
        return
    
    # APIキーのチェック
    if not api_key:
        print(f"エラー: {provider.upper()}_API_KEY が .env ファイルに"
              "設定されていません")
        print(f".env ファイルに {provider.upper()}_API_KEY="
              "your_actual_api_key を追加してください")
        return
    
    # 既存のファイル数をチェック
    folder_was_newly_created = not out.exists()
    ensure_dir(out)
    existing_files = list(Path(out).glob("*.jpg"))
    existing_count = len(existing_files)
    
    print(f"プロバイダー: {provider}")
    print(f"検索キーワード: {query}")
    print(f"保存先: {out}")
    print(f"既存ファイル数: {existing_count}")
    print(f"目標ファイル数: {n}")
    
    if existing_count >= n:
        print(f"✅ 既に {existing_count} 個のファイルがあります。"
              f"目標数 {n} に達済みです。")
        return
    
    additional_needed = n - existing_count
    print(f"追加ダウンロード予定: {additional_needed} 個")
    
    if min_width or min_height:
        print(f"最小サイズ: {min_width}x{min_height}")
    print("ダウンロード開始...")
    print()
    
    got = 0
    page = 1
    per_page = min(additional_needed, 80)
    rate_info_displayed = False
    search_info_displayed = False
    consecutive_empty_pages = 0
    max_empty_pages = 3  # 連続して空のページが続いた場合の上限
    while got < additional_needed:
        try:
            if provider == "pixabay":
                urls, rate_info, search_info = search_pixabay(
                    api_key, query, per_page, page, min_width, min_height
                )
                # 最初のリクエスト後にレート制限情報を表示
                if not rate_info_displayed:
                    display_rate_limit_info(rate_info)
                    rate_info_displayed = True
                # 検索結果情報の表示（最初のページのみ）
                if not search_info_displayed:
                    if not display_search_info(
                        search_info, provider, out, folder_was_newly_created
                    ):
                        return  # 検索結果がない場合は終了
                    search_info_displayed = True
                    print()
            else:
                urls, search_info = search_pexels(api_key, query, per_page, page)
                # 検索結果情報の表示（最初のページのみ）
                if not search_info_displayed:
                    if not display_search_info(
                        search_info, provider, out, folder_was_newly_created
                    ):
                        return  # 検索結果がない場合は終了
                    search_info_displayed = True
                    print()

            if not urls:
                consecutive_empty_pages += 1
                if consecutive_empty_pages >= max_empty_pages:
                    print(f"⚠️  連続して {max_empty_pages} ページに結果がありません。"
                          "検索を終了します。")
                    break
                print(f"📄 ページ {page}: 結果なし "
                      f"({consecutive_empty_pages}/{max_empty_pages})")
                page += 1
                continue
            else:
                consecutive_empty_pages = 0  # リセット

        except requests.exceptions.RequestException as e:
            print(f"❌ API リクエストエラー: {e}", file=sys.stderr)
            print("   ネットワーク接続を確認してください。", file=sys.stderr)
            break
        except Exception as e:
            print(f"❌ 予期しないエラー: {e}", file=sys.stderr)
            break

        for u in urls:
            try:
                fp = download(u, out)
                got += 1
                total_files = existing_count + got
                print(f"[{total_files}] {fp}")
                if got >= additional_needed:
                    break
                time.sleep(delay)
            except Exception as e:
                print(f"skip {u}: {e}", file=sys.stderr)
        page += 1

    final_count = existing_count + got
    if got > 0:
        print(f"✅ 完了: {got} 個の新しいファイルを追加しました")
        print(f"📁 総ファイル数: {final_count} 個 ({out})")
    else:
        print("❌ 新しいファイルをダウンロードできませんでした")
        if final_count > 0:
            print(f"📁 既存ファイル数: {final_count} 個 ({out})")
        else:
            # ダウンロードできず、既存ファイルもない場合、新規作成されたフォルダを削除
            cleanup_empty_folder(out, folder_was_newly_created)

if __name__ == "__main__":
    main()