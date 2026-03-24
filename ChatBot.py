from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import json
import re

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    lang: str = "ko"
    
# Mock language dictionary for pending responses
PENDING_REPLIES = {
    "ko": "죄송합니다. 현재 AI 기능이 준비 중입니다. 곧 답변을 드릴 수 있도록 하겠습니다! 🙏",
    "en": "Sorry, the AI feature is currently being prepared. We'll be able to answer soon! 🙏",
    "ja": "申し訳ございません。現在AI機能を準備中です。まもなくお答えできるようになります！🙏",
    "zh": "抱歉，AI功能正在准备中。我们很快就能为您解答！🙏",
    "vi": "Xin lỗi, tính năng AI đang được chuẩn bị. Chúng tôi sẽ sớm trả lời! 🙏",
    "es": "Lo siento, la función de IA está en preparación. ¡Pronto podremos responder! 🙏"
}

medication_data = []

def load_medication_data():
    global medication_data
    try:
        json_path = os.path.join(os.path.dirname(__file__), "userMedicationData.json")
        if os.path.exists(json_path):
            with open(json_path, "r", encoding="utf-8") as f:
                content = f.read()
                # Extract the JSON array part
                match = re.search(r'\[.*\]', content, re.DOTALL)
                if match:
                    array_str = match.group(0)
                    medication_data = json.loads(array_str)
    except Exception as e:
        print("Error loading medication data:", e)



# Initialize on startup
load_medication_data()

def get_medication_response(message: str) -> str:
    query = message.lower().replace(" ", "")
    
    # Check for specific medication by name
    for med in medication_data:
        full_name = med.get("name", "")
        clean_name = full_name.lower().replace(" ", "")
        
        if query and query in clean_name:
            return (
                f"💊 **{full_name}** 정보입니다.\n"
                f"- 분류: {med.get('category', '정보 없음')}\n"
                f"- 주의사항: {med.get('caution', '내용 없음')}\n"
                f"- 복용법: {med.get('description', '내용 없음')}"
            )

    # General queries (Limit to top 10 to avoid text flooding)
    if any(kw in query for kw in ["일정", "시간", "언제"]):
        response = "[ 기본 복약 일정 ]\n"
        for idx, med in enumerate(medication_data):
            if idx >= 10:
                response += "... (이하 생략)\n"
                break
            short_name = med.get("name", "").split('(')[0].strip()
            response += f"- {short_name}: {med.get('schedule', '미상')}\n"
        return response

    if any(kw in query for kw in ["주의", "부작용", "같이", "금기"]):
        response = "[ 복약 주의사항 ]\n"
        for idx, med in enumerate(medication_data):
            if idx >= 10:
                response += "... (이하 생략)\n"
                break
            short_name = med.get("name", "").split('(')[0].strip()
            response += f"- {short_name}: {med.get('caution', '없음')}\n"
        return response

    return None

@app.get("/", response_class=HTMLResponse)
async def get_chatbot_page():
    # Attempt to read ChatBot.html from the same directory
    html_path = os.path.join(os.path.dirname(__file__), "ChatBot.html")
    try:
        with open(html_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "<h1>ChatBot.html not found</h1>"

@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest):
    # Try finding an answer from the loaded medication data
    local_response = get_medication_response(req.message)
    if local_response:
        return {"reply": local_response}

    # This simulates a backend reply using the requested language
    reply = PENDING_REPLIES.get(req.lang, PENDING_REPLIES["ko"])
    return {"reply": reply}

# Keep the original dashboard APIs in case they are still needed
@app.get("/api/dashboard")
async def get_dashboard():
    return {
        "user_name": "홍길동",
        "stats": [
            {"label": "오늘 복약", "value": "3"},
            {"label": "남은 알림", "value": "1"},
            {"label": "연속 복약", "value": "7일"}
        ],
        "sections": [
            {
                "title": "💊 복약 관리",
                "items": [
                    {"title": "복약 일정", "icon": "clock", "to": "/schedule"},
                    {"title": "복용량 확인", "icon": "pill", "to": "/dosage"},
                    {"title": "잔여 약 확인", "icon": "package", "to": "/remaining"},
                    {"title": "캘린더", "icon": "calendar", "to": "/calendar"},
                ],
            },
            {
                "title": "🏥 건강 관리",
                "items": [
                    {"title": "증상/상태", "icon": "activity", "to": "/symptoms"},
                    {"title": "신체 정보", "icon": "users", "to": "/physical-info"},
                    {"title": "LLM 분석", "icon": "bar-chart-3", "to": "/analysis"},
                    {"title": "생활 가이드", "icon": "salad", "to": "/lifestyle"},
                ],
            },
            {
                "title": "🚨 긴급 & 안전",
                "items": [
                    {"title": "긴급 연락처", "icon": "phone", "to": "/emergency"},
                    {"title": "주의사항", "icon": "alert-triangle", "to": "/precautions"},
                ],
            }
        ]
    }

@app.post("/api/check-medication")
async def check_medication(med_id: str):
    return {"status": "success", "message": f"{med_id} 복약 완료 처리되었습니다."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
