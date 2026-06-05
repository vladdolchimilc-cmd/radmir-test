import time
import uvicorn
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse

app = FastAPI()

FRACTIONS = [
    "МВД (Полиция)", "МЗ (Медики)", "МО (Армия)", "ФСБ", 
    "Правительство", "МЧС", "ТРК (Ритм)", "ФСИН"
]

# Тестовые вопросы
CHOICE_QUESTIONS = [
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
        "text": "Каков минимальный интервал между подачей своих строк в государственную волну (/gov) одной организации?",
        "options": ["3 минуты", "5 минут", "10 минут", "15 минут"],
        "correct": "10 минут"
    },
    {
        "id": 4,
        "text": "Какое максимальное количество заместителей (9 рангов) может быть в организации одновременно?",
        "options": ["1", "2", "3", "4"],
        "correct": "3"
    },
    {
        "id": 5,
        "text": "Разрешено ли использовать нецензурную брань (мат) в чат департамента (/d)?",
        "options": ["Да, в рамках RP процесса", "Запрещено в любом виде (как в IC, так и в OOC)", "Разрешено, если закрыть тему через (())", "Разрешено только лидеру"],
        "correct": "Запрещено в любом виде (как в IC, так и в OOC)"
    }
]

# Письменные вопросы (будут выведены в конце)
TEXT_QUESTIONS = [
    {
        "id": 6,
        "text": "Опишите своими словами, что такое 'Блат' в государственных организациях и как вы будете с ним бороться?"
    },
    {
        "id": 7,
        "text": "Сформулируйте правила и основные запреты при использовании чата департамента (/d) для заместителей."
    },
    {
        "id": 8,
        "text": "Расшифруйте термины и приведите примеры нарушений для каждого: SK, TK, RK, PG."
    }
]

PASS_SCORE_PERCENT = 80

@app.get("/", response_class=HTMLResponse)
async def get_test_page():
    start_time = time.time()
    fraction_options = "".join([f"<option value='{f}'>{f}</option>" for f in FRACTIONS])

    # Генерируем карточки для тестовых вопросов
    steps_html = ""
    step_index = 2  # Шаг 1 — это ввод ника и фракции

    for q in CHOICE_QUESTIONS:
        options_html = ""
        for opt in q["options"]:
            options_html += f"""
            <label class="option-card">
                <input type="radio" name="q_{q['id']}" value="{opt}" style="margin-right: 15px; accent-color: #ff4500;">
                <span>{opt}</span>
            </label>
            """
        steps_html += f"""
        <div class="step-content" id="step-{step_index}" style="display: none;">
            <div class="question-header">Вопрос {step_index - 1} из {len(CHOICE_QUESTIONS) + len(TEXT_QUESTIONS)}</div>
            <p class="question-text">{q['text']}</p>
            <div class="options-container">{options_html}</div>
            <div class="btn-group">
                <button type="button" class="btn btn-secondary" onclick="prevStep({step_index})">Назад</button>
                <button type="button" class="btn btn-primary" onclick="nextStep({step_index})">Далее</button>
            </div>
        </div>
        """
        step_index += 1

    # Генерируем карточки для письменных вопросов
    for q in TEXT_QUESTIONS:
        steps_html += f"""
        <div class="step-content" id="step-{step_index}" style="display: none;">
            <div class="question-header">Письменный вопрос {step_index - 1} из {len(CHOICE_QUESTIONS) + len(TEXT_QUESTIONS)}</div>
            <p class="question-text">{q['text']}</p>
            <textarea name="q_{q['id']}" placeholder="Введите ваш развернутый ответ здесь (минимум 20 символов)..." class="text-answer" rows="6"></textarea>
            <div class="btn-group">
                <button type="button" class="btn btn-secondary" onclick="prevStep({step_index})">Назад</button>
                {"<button type='button' class='btn btn-primary' onclick='nextStep(" + str(step_index) + ")'>Далее</button>" if step_index < (len(CHOICE_QUESTIONS) + len(TEXT_QUESTIONS) + 1) else ""}
                {"<button type='submit' class='btn btn-submit'>Завершить тестирование</button>" if step_index == (len(CHOICE_QUESTIONS) + len(TEXT_QUESTIONS) + 1) else ""}
            </div>
        </div>
        """
        step_index += 1

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>ПРОТОКОЛ ТЕСТИРОВАНИЯ | RADMIR RP</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{
                font-family: 'Courier New', Courier, monospace;
                background: #0a0a0f;
                color: #00ff66;
                margin: 0;
                padding: 20px;
            }}
            .terminal-container {{
                max-width: 750px;
                margin: 40px auto;
                background: #0f1015;
                padding: 40px;
                border-radius: 4px;
                box-shadow: 0 0 20px rgba(255, 69, 0, 0.15);
                border: 2px solid #222530;
            }}
            .terminal-header {{
                text-align: center;
                margin-bottom: 40px;
                border-bottom: 2px dashed #222530;
                padding-bottom: 20px;
            }}
            .terminal-title {{
                color: #ff4500;
                margin: 0;
                font-size: 24px;
                text-transform: uppercase;
                letter-spacing: 2px;
                text-shadow: 0 0 10px rgba(255, 69, 0, 0.3);
            }}
            .terminal-subtitle {{
                color: #6c738c;
                margin-top: 10px;
                font-size: 13px;
            }}
            .input-field, .select-field {{
                width: 100%;
                padding: 14px;
                background: #14161f;
                border: 1px solid #303545;
                border-radius: 4px;
                color: #fff;
                font-size: 16px;
                box-sizing: border-box;
                font-family: inherit;
            }}
            .input-field:focus, .select-field:focus {{
                outline: none;
                border-color: #ff4500;
                box-shadow: 0 0 8px rgba(255, 69, 0, 0.2);
            }}
            .question-header {{
                color: #ff4500;
                font-size: 14px;
                margin-bottom: 10px;
                text-transform: uppercase;
                letter-spacing: 1px;
            }}
            .question-text {{
                font-size: 18px;
                color: #fff;
                margin-top: 0;
                margin-bottom: 25px;
                line-height: 1.5;
            }}
            .option-card {{
                display: flex;
                align-items: center;
                margin: 12px 0;
                padding: 15px;
                background: #14161f;
                border: 1px solid #222530;
                border-radius: 4px;
                cursor: pointer;
                transition: 0.2s;
                color: #c4c9de;
            }}
            .option-card:hover {{
                border-color: #ff4500;
                background: #191b26;
            }}
            .text-answer {{
                width: 100%;
                background: #14161f;
                border: 1px solid #303545;
                border-radius: 4px;
                color: #fff;
                padding: 15px;
                font-size: 15px;
                box-sizing: border-box;
                font-family: inherit;
                resize: none;
            }}
            .text-answer:focus {{
                outline: none;
                border-color: #ff4500;
            }}
            .btn-group {{
                display: flex;
                justify-content: space-between;
                margin-top: 30px;
                gap: 15px;
            }}
            .btn {{
                padding: 14px 28px;
                border: none;
                border-radius: 4px;
                font-size: 14px;
                font-weight: bold;
                cursor: pointer;
                text-transform: uppercase;
                font-family: inherit;
                transition: 0.2s;
            }}
            .btn-primary {{ background: #ff4500; color: #fff; }}
            .btn-primary:hover {{ background: #e03d00; }}
            .btn-secondary {{ background: #222530; color: #8a91a8; }}
            .btn-secondary:hover {{ background: #2d3142; color: #fff; }}
            .btn-submit {{ background: #00ff66; color: #000; width: 100%; }}
            .btn-submit:hover {{ background: #00e65c; }}
            .form-label {{
                display: block;
                margin-bottom: 10px;
                color: #ff4500;
                font-size: 14px;
                text-transform: uppercase;
            }}
        </style>
    </head>
    <body>
        <div class="terminal-container">
            <div class="terminal-header">
                <h2 class="terminal-title">■ ДЕПАРТАМЕНТ КОНТРОЛЯ КАДРОВ ■</h2>
                <p class="terminal-subtitle">Квалификационный экзамен на руководящую должность (9 ранг)</p>
            </div>
            
            <form action="/submit" method="post" id="quiz-form">
                <input type="hidden" name="start_time" value="{start_time}">

                <!-- ШАГ 1: АВТОРИЗАЦИЯ -->
                <div class="step-content" id="step-1">
                    <div style="margin-bottom: 25px;">
                        <label class="form-label">> Идентификация кандидата (Никнейм):</label>
                        <input type="text" id="nick-input" name="nickname" placeholder="Имя_Фамилия" required class="input-field">
                    </div>
                    
                    <div style="margin-bottom: 35px;">
                        <label class="form-label">> Ведомственная структура (Организация):</label>
                        <select id="frac-input" name="fraction" required class="select-field">
                            <option value="" disabled selected>-- ВЫБЕРИТЕ ИЗ СПИСКА --</option>
                            {fraction_options}
                        </select>
                    </div>
                    <button type="button" class="btn btn-primary" style="width: 100%;" onclick="startQuiz()">Инициализировать тест</button>
                </div>
                
                <!-- ТЕСТОВЫЕ И ПИСЬМЕННЫЕ ВОПРОСЫ (ГЕНЕРИРУЮТСЯ СКРИПТОМ) -->
                {steps_html}
            </form>
        </div>

        <script>
            function startQuiz() {{
                const nick = document.getElementById('nick-input').value.trim();
                const frac = document.getElementById('frac-input').value;
                if(!nick || !frac) {{
                    alert("ОШИБКА: Заполните все поля авторизации.");
                    return;
                }}
                document.getElementById('step-1').style.display = 'none';
                document.getElementById('step-2').style.display = 'block';
            }}

            function nextStep(currentStep) {{
                // Проверка, выбран ли ответ на текущем тестовом шаге
                const inputs = document.querySelectorAll(`#step-${{currentStep}} input[type="radio"]`);
                if(inputs.length > 0) {{
                    let checked = false;
                    inputs.forEach(i => {{ if(i.checked) checked = true; }});
                    if(!checked) {{
                        alert("СИСТЕМНОЕ УВЕДОМЛЕНИЕ: Выберите один из вариантов ответа.");
                        return;
                    }}
                }}
                
                // Проверка, заполнен ли письменный ответ
                const textarea = document.querySelector(`#step-${{currentStep}} textarea`);
                if(textarea && textarea.value.trim().length < 20) {{
                    alert("СИСТЕМНОЕ УВЕДОМЛЕНИЕ: Ваш ответ слишком короткий (минимум 20 символов для развернутого ответа).");
                    return;
                }}

                document.getElementById(`step-${{currentStep}}`).style.display = 'none';
                document.getElementById(`step-${{currentStep + 1}}`).style.display = 'block';
            }}

            function prevStep(currentStep) {{
                document.getElementById(`step-${{currentStep}}`).style.display = 'none';
                document.getElementById(`step-${{currentStep - 1}}`).style.display = 'block';
            }}
        </script>
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
    total_choice = len(CHOICE_QUESTIONS)
    
    for q in CHOICE_QUESTIONS:
        user_answer = form_data.get(f"q_{q['id']}")
        if user_answer == q["correct"]:
            correct_count += 1
            
    score_percent = round((correct_count / total_choice) * 100)
    is_passed = score_percent >= PASS_SCORE_PERCENT
    
    status_style = "background: #052e16; color: #00ff66; border: 1px solid #14532d;" if is_passed else "background: #450a0a; color: #ef4444; border: 1px solid #7f1d1d;"
    status_text = "🟢 ОДОБРЕНО (Тестовая часть пройдена)" if is_passed else "🔴 ОТКАЗАНО (Тестовая часть завалена)"

    # Формируем блок с письменными ответами для проверки лидером
    written_answers_html = ""
    for q in TEXT_QUESTIONS:
        ans = form_data.get(f"q_{q['id']}", "Нет ответа")
        written_answers_html += f"""
        <div style="margin-top: 15px; padding: 12px; background: #14161f; border-left: 3px solid #ff4500; border-radius: 4px;">
            <p style="margin: 0 0 8px 0; color: #ff4500; font-weight: bold;">Вопрос: {q['text']}</p>
            <p style="margin: 0; color: #fff; font-style: italic;">Ответ: {ans}</p>
        </div>
        """

    result_html = f"""
    <!DOCTYPE html>
    <html>
    <head><title>ПРОТОКОЛ ОБРАБОТАН</title><meta charset="utf-8"></head>
    <body style="font-family: 'Courier New', monospace; background: #0a0a0f; color: #fff; padding: 40px 20px;">
        <div style="max-width: 650px; margin: 40px auto; background: #0f1015; padding: 40px; border-radius: 4px; border: 2px solid #222530; box-shadow: 0 0 20px rgba(0,255,102,0.1);">
            <h2 style="text-align: center; color: #ff4500; margin-top: 0; text-transform: uppercase; letter-spacing: 1px;">■ СИСТЕМНЫЙ РЕЗУЛЬТАТ ■</h2>
            <hr style="border: 0; border-top: 2px dashed #222530; margin: 20px 0;">
            
            <div style="font-size: 15px; line-height: 1.8; color: #c4c9de;">
                <p><b>[👤 КАНДИДАТ]:</b> <span style="color: #ff4500;">{nickname}</span></p>
                <p><b>[🏢 СТРУКТУРА]:</b> {fraction}</p>
                <p><b>[⏱️ ВРЕМЯ НА ОТВЕТЫ]:</b> {time_str}</p>
                <p><b>[📊 ТЕСТОВЫЙ БАЛЛ]:</b> {correct_count} из {total_choice} ({score_percent}%)</p>
            </div>
            
            <div style="margin-top: 25px; padding: 15px; border-radius: 4px; text-align: center; font-size: 16px; font-weight: bold; {status_style}">
                {status_text}
            </div>

            <h3 style="color: #ff4500; margin-top: 35px; text-transform: uppercase; font-size: 15px;">■ БЛОК ПИСЬМЕННЫХ ОТВЕТОВ:</h3>
            {written_answers_html}
            
            <p style="text-align: center; color: #6c738c; font-size: 12px; margin-top: 40px;">Данные сохранены в кэш-памяти сессии. Передайте протокол лидеру организации.</p>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=result_html)

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
