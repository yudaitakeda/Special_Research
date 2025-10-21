import os
import re
import requests
from bs4 import BeautifulSoup

class AozoraCardFetcher:
    def __init__(self):
        # 設定（ここで一括定義）
        self.base_url = "https://www.aozora.gr.jp"
        self.author_id = "148"
        self.author_name = "夏目漱石"
        self.author_page = f"{self.base_url}/index_pages/person{self.author_id}.html"
        self.card_urls = []

        sanitized_name = re.sub(r'[\\/*?:"<>|]', '_', self.author_name)
        self.download_folder = f"./data/files/text/{sanitized_name}"
        if not os.path.isdir(self.download_folder):
            os.makedirs(self.download_folder)


        # 起動時にすべて実行
        self.fetch_cards()
        for card_url in self.card_urls:
            print(f"[INFO] {card_url} から .html ファイルを取得中...")
            html_files = self.fetch_html_links_from_card(card_url)
            self.download_and_convert_html_files(html_files)

    def fetch_cards(self):
        res = requests.get(self.author_page)
        soup = BeautifulSoup(res.content, "html.parser")
        for li in soup.select("ol > li > a"):
            href = li.get("href")
            if href and "cards" in href and href.endswith(".html"):
                full_url = self.base_url + href.replace("..", "")
                self.card_urls.append(full_url)

    def fetch_html_links_from_card(self, card_url):
        res = requests.get(card_url)
        soup = BeautifulSoup(res.content, "html.parser")
        table = soup.find("table", class_="download")
        if not table:
            return []
        links = []
        for a in table.find_all("a"):
            href = a.get("href")
            if href and href.endswith(".html"):
                links.append(href.replace("./files/", ""))
        return links

    def clean_html_header(self, content):
        content = re.sub(r'<\?xml[^>]*?\?>', '', content)
        content = re.sub(r'<!DOCTYPE[^>]*?>', '<!DOCTYPE html>', content)
        content = re.sub(r'<html[^>]*?xml:lang="ja"[^>]*?>', '<html lang="ja">', content)
        content = content.replace(
            '<meta http-equiv="Content-Type" content="text/html;charset=Shift_JIS" />',
            '<meta http-equiv="content-type" content="text/html; charset=UTF-8" />\n<meta name="viewport" content="width=device-width, initial-scale=1.0" />'
        )
        content = content.replace(
            '<link rel="stylesheet" type="text/css" href="../../default.css" />',
            '<link rel="stylesheet" type="text/css" href="../../viewer/css/style.css" />'
        )
        content = content.replace(
            '<link rel="stylesheet" type="text/css" href="../../aozora.css" />',
            '<link rel="stylesheet" type="text/css" href="../../viewer/css/style.css" />'
        )
        content = re.sub(r'(<meta[^>]*?)(?<!/)>', r'\1 />', content)
        content = re.sub(r'</meta>', '', content)
        content = re.sub(r'(<link[^>]*?)(?<!/)>', r'\1 />', content)
        content = re.sub(r'</link>', '', content)
        content = re.sub(r'^\s*\n', '', content, flags=re.MULTILINE)
        return content

    def extract_title(self, html_content):
        soup = BeautifulSoup(html_content, "html.parser")
        title_tag = soup.find("title")
        if title_tag:
            full_title = title_tag.text.strip()
            cleaned_title = re.sub(f'^{re.escape(self.author_name)}\\s*', '', full_title)
            return cleaned_title
        return "unknown_title"

    def sanitize_filename(self, title):
        return re.sub(r'[\\/*?:"<>|]', '_', title)

    def download_and_convert_html_files(self, html_files):
        for file_name in html_files:
            download_url = f"{self.base_url}/cards/{int(self.author_id):06}/files/{file_name}"

            try:
                response = requests.get(download_url)
                response.encoding = 'shift_jis'
                original_html = response.text
                converted_html = self.clean_html_header(original_html)
                title = self.extract_title(original_html)
                safe_title = self.sanitize_filename(title)
                output_path = os.path.join(self.download_folder, f"{safe_title}.html")

                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(converted_html)
                print(f"✅ {safe_title}.html を保存しました。")

            except requests.exceptions.RequestException as e:
                print(f"⚠️ ダウンロード失敗: {file_name} - {e}")


if __name__ == "__main__":
    AozoraCardFetcher()