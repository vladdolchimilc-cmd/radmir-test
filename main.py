import time
import uvicorn
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse

app = FastAPI()

FRACTIONS = [
    "МВД (Полиция)", 
    "МЗ (Медики)", 
    "МО (Армия)", 
    "ФСБ", 
    "Правительство", 
    "МЧС", 
    "ТРК (Ритм)", 
    "ФСИН"
]

# Расширенный список вопросов для качественной проверки
QUESTIONS = [
    {
        "id": 1,
        "text": "Каков минимальный игровой уровень для занятия поста заместителя?",
        "options": ["5 уровень", "10 уровень", "15 уровень", "Нет ограничений"],
        "correct": "10 уровень"
    },
    {
        "id": 2,
        "text": "Что обязан сделать заместитель при уходе со своего поста ПСЖ, если не отстоял минимальный срок (7 дней)?",
        "options": ["Ничего, это право игрока", "Получить варн или бан", "Заплатить штраф лидеру", "Понизиться на 1 ранг"],
        "correct": "Получить варн или бан"
    },
    {
        "id": 3,
        "text": "Разрешено ли заместителю принимать людей во фракцию без электронного заявления или собеседования (блат)?",
        "options": ["Да, если это доверенное лицо", "Да, на усмотрение лидера", "Категорически запрещено", "Разрешено до 3 ранга"],
        "correct": "Категорически запрещено"
    },
    {
        "id": 4,
        "text": "Каков минимальный интервал между подачей своих строк в государственную волну (/gov) одной организации?",
        "options": ["3 минуты", "5 минут", "10 минут", "15 минут"],
        "correct": "10 минут"
    },
    {
        "id": 5,
        "text": "Разрешено ли занимать гос. волну (/gov) за несколько часов до подачи вещания?",
        "options": ["Да, хоть за сутки", "Максимум за 30 минут", "Максимум за 20 минут", "Разрешено только за 10-15 минут"],
        "correct": "Разрешено только за 10-15 минут"
    },
    {
        "id": 6,
        "text": "Что такое 'Блат' в понимании правил государственных организаций?",
        "options": ["Повышение за хорошую работу", "Знакомство, связи, используемые в личных интересах в ущерб службе", "Выдача выговора за нарушение устава", "Проведение совместной тренировки"],
        "correct": "Знакомство, связи, используемые в личных интересах в ущерб службе"
    },
    {
        "id": 7,
        "text": "Какое максимальное количество заместителей (9 рангов) может быть в организации одновременно?",
        "options": ["1", "2", "3", "4"],
        "correct": "3"
    },
    {
        "id": 8,
        "text": "Разрешено ли использовать нецензурную брань (мат) в чат департамента (/d)?",
        "options": ["Да, в рамках RP процесса", "Запрещено в любом виде (как в IC, так и в OOC)", "Разрешено, если закрыть тему через (())", "Разрешено только лидеру"],
        "correct": "Запрещено в любом виде (как в IC, так и в OOC)"
    },
    {
        "id": 9,
        "text": "Какое наказание следует за слив глобального чата фракции или гос. волны?",
        "options": ["Устное предупреждение", "Выговор от лидера", "Блокировка аккаунта (Бан) + ЧС ГОС", "Понижение в должности"],
        "correct": "Блокировка аккаунта (Бан) + ЧС ГОС"
    },
    {
        "id": 10,
        "text": "Имеет ли право заместитель игнорировать приказы и указы Губернатора/Директора ФСБ (в рамках закона)?",
        "options": ["Да, заместитель подчиняется только своему лидеру", "Нет, они являются высшим руководством области", "Да, если заместитель работает в МЗ или МЧС", "Только во время обеденного перерыва"],
        "correct": "Нет, они являются высшим руководством области"
    }
]

# Для сдачи нужно ответить правильно минимум на 8 из 10 вопросов (80%)
PASS_SCORE_PERCENT = 80

@app.get("/", response_class=HTMLResponse)
async def get_test_page():
    start_time = time.time()
    fraction_options = "".join([f"<option value='{f}'>{f}</option>" for f in FRACTIONS])

    questions_html = ""
    for q in QUESTIONS:
        options_html = ""
        for opt in q["options"]:
            options_html += f"""
            <label style="display: flex; align-items: center; margin: 12px 0; padding: 10px; background: #2a2a35; border: 1px solid #3a3a4a; border-radius: 6px; cursor: pointer; transition: 0.2s; color: #e0e0e0;">
                <input type="radio" name="q_{q['id']}" value="{opt}" required style="margin-right: 12px; accent-color: #ff4500;">
                <span>{opt}</span>
            </label>
            """
        questions_html += f"""
        <div style="background: #22222b; padding: 20px; margin-bottom: 20px; border-left: 5px solid #ff4500; border-radius: 6px; box-shadow: 0 2px 5px rgba(0,0,0,0.2);">
            <p style="font-weight: bold; font-size: 16px; color: #fff; margin-top: 0; margin-bottom: 15px;">{q['id']}. {q['text']}</p>
            {options_html}
        </div>
        """

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Система Тестирования | Radmir RP</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #18181f; color: #fff; margin: 0; padding: 20px;">
        <div style="max-width: 700px; margin: 40px auto; background: #1c1c24; padding: 40px; border-radius: 12px; box-shadow: 0 10px 25px rgba(0,0,0,0.5); border: 1px solid #2d2d3d;">
            <div style="text-align: center; margin-bottom: 30px;">
                <h2 style="color: #ff4500; margin: 0; font-size: 28px; text-transform: uppercase; letter-spacing: 1px;">🔥 Проверка Государственных Служащих</h2>
                <p style="color: #8a8a9e; margin-top: 10px; font-size: 15px;">Официальный тест на знание правил для кандидатов на пост Заместителя (9)</p>
            </div>
            
            <hr style="border: 0; border-top: 1px solid #2d2d3d; margin: 30px 0;">
            
            <form action="/submit" method="post">
                <input type="hidden" name="start_time" value="{start_time}">

                <div style="margin-bottom: 25px;">
                    <label style="font-weight: bold; color: #ff4500; display: block; margin-bottom: 8px;">👤 Ваш Игровой Никнейм (Имя_Фамилия):</label>
                    <input type="text" name="nickname" placeholder="Например: Dmitry_Kabanov" required style="width: 100%; padding: 12px; background: #22222b; border: 1px solid #3a3a4a; border-radius: 6px; color: #fff; font-size: 15px; box-sizing: border-box;">
                </div>
                
                <div style="margin-bottom: 35px;">
                    <label style="font-weight: bold; color: #ff4500; display: block; margin-bottom: 8px;">🏢 Организация, на которую подаете:</label>
                    <select name="fraction" required style="width: 100%; padding: 12px; background: #22222b; border: 1px solid #3a3a4a; border-radius: 6px; color: #fff; font-size: 15px; box-sizing: border-box; cursor: pointer;">
                        <option value="" disabled selected>-- Выберите фракцию из списка --</option>
                        {fraction_options}
                    </select>
                </div>
                
                <h3 style="color: #fff; border-bottom: 1px solid #2d2d3d; padding-bottom: 10px; margin-bottom: 20px;">Раздел: Вопросы на проверку знаний</h3>
                
                {questions_html}
                
                <button type="submit" style="width: 100%; background: #ff4500; color: white; padding: 16px; border: none; border-radius: 6px; font-size: 16px; font-weight: bold; cursor: pointer; text-transform: uppercase; letter-spacing: 1px; transition: 0.3s; margin-top: 15px; box-shadow: 0 4px 15px rgba(255, 69, 0, 0.4);">Отправить ответы на проверку</button>
            </form>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.post("/submit", response_class=HTMLResponse)
async def handle_submit(
    request: Request,
    nickname: str = Form(...),
    fraction: str = Form(...),
    start_time: float = Form(...)
):
    end_time = time.time()
    duration_seconds = int(end_time - start_time)
    
    minutes = duration_seconds // 60
    seconds = duration_seconds % 60
    time_str = f"{minutes} мин. {seconds} сек." if minutes > 0 else f"{seconds} сек."

    form_data = await request.form()
    correct_count = 0
    total_questions = len(QUESTIONS)
    
    for q in QUESTIONS:
        user_answer = form_data.get(f"q_{q['id']}")
        if user_answer == q["correct"]:
            correct_count += 1
            
    score_percent = round((correct_count / total_questions) * 100)
    is_passed = score_percent >= PASS_SCORE_PERCENT
    
    status_style = "background: #1b4332; color: #52b788; border: 1px solid #2d6a4f;" if is_passed else "background: #4c1d1d; color: #ff6b6b; border: 1px solid #7a2222;"
    status_text = "🟢 ОДОБРЕНО (Тест успешно сдан)" if is_passed else "🔴 ОТКАЗАНО (Недостаточно баллов)"

    result_html = f"""
    <!DOCTYPE html>
    <html>
    <head><title>Результаты проверки</title><meta charset="utf-8"></head>
    <body style="font-family: 'Segoe UI', sans-serif; background: #18181f; color: #fff; padding: 40px 20px;">
        <div style="max-width: 600px; margin: 50px auto; background: #1c1c24; padding: 40px; border-radius: 12px; box-shadow: 0 10px 25px rgba(0,0,0,0.5); border: 1px solid #2d2d3d;">
            <h2 style="text-align: center; color: #ff4500; margin-top: 0; text-transform: uppercase;">📑 Протокол результатов</h2>
            <hr style="border: 0; border-top: 1px solid #2d2d3d; margin: 20px 0;">
            
            <div style="font-size: 16px; line-height: 1.8;">
                <p><b>👤 Кандидат:</b> <span style="color: #ff4500;">{nickname}</span></p>
                <p><b>🏢 Целевая организация:</b> {fraction}</p>
                <p><b>⏱️ Время на ответы:</b> {time_str}</p>
                <p><b>📊 Правильные ответы:</b> {correct_count} из {total_questions} (<span style="color: #ff4500;">{score_percent}%</span>)</p>
            </div>
            
            <div style="margin-top: 30px; padding: 20px; border-radius: 8px; text-align: center; font-size: 18px; font-weight: bold; {status_style}">
                {status_text}
            </div>
            
            <p style="text-align: center; color: #8a8a9e; font-size: 13px; margin-top: 30px;">Результат зафиксирован сервером системы тестирования Radmir RP.</p>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=result_html)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
