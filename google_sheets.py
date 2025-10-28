import gspread
from google.oauth2.service_account import Credentials

# Google Sheets API の設定
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SERVICE_ACCOUNT_FILE = "gen-lang-client-0633455094-14e2f973fc17.json"  # JSON鍵ファイル名

# あなたのスプレッドシートIDに置き換えて！
SPREADSHEET_ID = "https://docs.google.com/spreadsheets/d/1RggDXwvr93lLRYq_-JOgZZMRnHsbsTr5fV34mL6WgZ4/edit?gid=0#gid=0"

# 認証処理
credentials = Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)
gc = gspread.authorize(credentials)
sheet = gc.open_by_key(SPREADSHEET_ID).sheet1

# データをスプレッドシートに書き込む関数
def add_sleep_record(user_id, sleep_start, sleep_end, advice):
    sheet.append_row([user_id, sleep_start, sleep_end, advice])
