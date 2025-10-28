import os
import json
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
import gspread
from google.oauth2.service_account import Credentials
from google_sheets import add_sleep_record
import requests
import openai

# .envの読み込み
load_dotenv()

# -------------------------
# 🌍 環境変数
# -------------------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")

openai.api_key = OPENAI_API_KEY

# -------------------------
# 🧾 Googleスプレッドシート接続設定
# -------------------------
# credentials.json の読み込み
creds_info = json.loads(os.getenv("GOOGLE_CREDENTIALS"))
creds = Credentials.from_service_account_info(
    creds_info,
    scopes=[
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/drive"
    ]
)
client_gs = gspread.authorize(creds)

# スプレッドシート作成 or 取得
SHEET_NAME = "sleep_data"
try:
    sheet = client_gs.open(SHEET_NAME).sheet1
except gspread.SpreadsheetNotFound:
    sh = client_gs.create(SHEET_NAME)
    sh.share('', perm_type='anyone', role='writer')
    sheet = sh.sheet1
    sheet.append_row(["user_id", "sleep_start", "sleep_end", "advice"])

# -------------------------
# 🚀 FastAPI設定
# -------------------------
app = FastAPI()

class SleepData(BaseModel):
    user_id: str
    sleep_start: str
    sleep_end: str

# -------------------------
# 🧠 ChatGPTにアドバイスを生成させる関数
# -------------------------
def generate_advice(sleep_start, sleep_end):
    prompt = f"""
    以下の睡眠データをもとに、ユーザーに1〜2文の睡眠改善アドバイスをください。
    - 就寝時間: {sleep_start}
    - 起床時間: {sleep_end}
    """

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "あなたは優しい睡眠コーチです。"},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print("OpenAI API error:", e)
        return "AIによるアドバイスの生成に失敗しました。"

# -------------------------
# 💬 LINE通知送信関数
# -------------------------
def send_line_message(user_id, message):
    try:
        url = "https://api.line.me/v2/bot/message/push"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"
        }
        payload = {
            "to": user_id,
            "messages": [{"type": "text", "text": message}]
        }
        requests.post(url, headers=headers, json=payload)
    except Exception as e:
        print("LINE送信エラー:", e)

# -------------------------
# 📥 エンドポイント：/sleep
# -------------------------
@app.post("/sleep")
async def record_sleep(data: SleepData):
    advice = generate_advice(data.sleep_start, data.sleep_end)  # ChatGPT部分
    add_sleep_record(data.user_id, data.sleep_start, data.sleep_end, advice)
    return {"message": "Data added to Google Sheets", "advice": advice}
