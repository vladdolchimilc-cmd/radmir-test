import time
import httpx
import uvicorn
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse

app = FastAPI()

FRACTIONS = [
    "МВД (Полиция)", "МЗ (Медики)", "МО (Армия)", "ФСБ", 
    "Правительство", "МЧС", "ТРК (Ритм)", "ФСИН"
]

# 10 Жестких тестовых вопросов по твоим правилам
CHOICE_QUESTIONS = [
    {
        "id": 1,
        "text": "Каковы минимальные требования к оформлению правильной команды /try?",
        "options": [
            "С большой буквы и с точкой на конце",
            "С маленькой буквы и без точки на конце",
            "Без вопросительных знаков или иных знаков пунктуации (. , ? ! : )",
            "С обязательным знаком вопроса на конце"
        ],
        "correct": "Без вопросительных знаков или иных знаков пунктуации (. , ? ! : )"
    },
    {
        "id": 2,
        "text": "Каковы минимальные требования к длительности и объему скриншотов для зачета обычной RP ситуации?",
        "options": [
            "Минимум 5 скриншотов и 5 минут длительности",
            "Минимум 7 скриншотов и не менее 10 минут длительности по /c 60",
            "Достаточно 3 скриншотов без учета времени",
            "Минимум 10 скриншотов и 20 минут длительности"
        ],
        "correct": "Минимум 7 скриншотов и не менее 10 минут длительности по /c 60"
    },
    {
        "id": 3,
        "text": "Каков максимальный срок хранения скриншотов для подачи отчетов в государственные структуры?",
        "options": ["24 часа (1 день)", "48 часов (2 дня)", "72 часа (3 дня)", "7 дней"]
    },
    {
        "id": 4,
        "text": "В какое время разрешено проводить плановые и повторные проверки организаций?",
        "options": [
            "В любое время в течение рабочего дня",
            "Строго с 14:00 до конца рабочего дня",
            "С 10:00 до 18:00",
            "Только во время обеденного перерыва"
        ],
        "correct": "Строго с 14:00 до конца рабочего дня"
    },
    {
        "id": 5,
        "text": "Какое минимальное количество сотрудников должно быть в сети у обеих организаций для проведения проверки?",
        "options": [
            "Минимум 3 сотрудника с каждой стороны",
            "Минимум 5 сотрудников, включая проводящего",
            "Минимум 4 человека с обеих сторон (не включая человека, принявшего проверку)",
            "Ограничений по составу нет, главное присутствие 8+ ранга"
        ],
        "correct": "Минимум 4 человека с обеих сторон (не включая человека, принявшего проверку)"
    },
    {
        "id": 6,
        "text": "С какого ранга сотрудникам разрешено пользоваться рацией департамента (/d)?",
        "options": [
            "С 5-го ранга (Исключение: ФСИН/ФСБ с 3+ ранга)",
            "Строго с 8-го ранга для всех фракций",
            "С 4-го ранга для всех фракций без исключений",
            "Только Лидеру и его Заместителям (9-10 ранги)"
        ],
        "correct": "С 5-го ранга (Исключение: ФСИН/ФСБ с 3+ ранга)"
    },
    {
        "id": 7,
        "text": "Сотрудник МВД собирается провести задержание гражданина. Какое его первое действие по правилам?",
        "options": [
            "Сразу надеть наручники и провести обыск",
            "Обязан запросить документы подозреваемого (Исключение: лично видел нарушение, 5+ звезд, фоторобот)",
            "Открыть огонь на поражение для обездвиживания",
            "Выдать розыск по КПК, не приближаясь к игроку"
        ],
        "correct": "Обязан запросить документы подозреваемого (Исключение: лично видел нарушение, 5+ звезд, фоторобот)"
    },
    {
        "id": 8,
        "text": "В каких временных рамках разрешено проводить собеседования во фракции по /c 060?",
        "options": ["Круглосуточно", "С 8:00 до 22:00", "С 7:00 до 00:00", "Строго с 12:00 до 21:00"],
        "correct": "С 7:00 до 00:00"
    },
    {
        "id": 9,
        "text": "Какое из указанных действий НЕ является блатом со стороны руководства?",
        "options": [
            "Повышение сотрудника на 2 ранга за один день",
            "Принятие человека на Заместителя по доверию при свободном месте в начале срока (согласовав с адм)",
            "Восстановление сотрудника на прежний ранг после получения им Warn'а",
            "Принятие гражданина в организацию в обход ЧС фракции"
        ],
        "correct": "Принятие человека на Заместителя по доверию при свободном месте в начале срока (согласовав с адм)"
    },
    {
        "id": 10,
        "text": "Что произойдет, если заместитель уйдет со своего поста по СЖ, не отстояв минимальный срок (7 дней)?",
        "options": [
            "Его просто уволят без наказаний",
            "Он получит предупреждение (Варн) или Блокировку аккаунта (Бан)",
            "Ему понизят законопослушность до 0",
            "Он будет переведен рядовым в Министерство Обороны"
        ],
        "correct": "Он получит предупреждение (Варн) или Блокировку аккаунта (Бан)"
    }
]

# 5 Сложных письменных ситуаций
TEXT_QUESTIONS = [
    {
        "id": 11,
        "text": "Ситуация: Вы проводите проверку МЗ. При проверке сан. норм выпало много попыток 'Неудачно', а у одного сотрудника обнаружен розыск. Рассчитайте по правилам из текста, сколько баллов вы отнимете из оценки фракции?"
    },
    {
        "id": 12,
        "text": "Напишите пример ИДЕАЛЬНОЙ и грамотной цепочки отыгровок команд /me, /do и /try для обыска подозреваемого на наличие запрещенных веществ, строго соблюдая правила регистров и точек."
    },
    {
        "id": 13,
        "text": "Вам необходимо перевести вещание в гос. волну (/gov). Опишите правила занятия линии: за сколько минут занимается, какой минимальный интервал между вещаниями одной фракции и правила заполнения."
    },
    {
        "id": 14,
        "text": "Вы стоите на посту Заместителя ТРК 'Ритм'. Старший состав собрал строй, при этом в здании не осталось ни одного сотрудника 2+ ранга для редактирования объявлений, а очередь /edit превысила 15 штук. Каковы ваши действия и какое правило здесь нарушено?"
    },
    {
        "id": 15,
        "text": "Опишите подробные правила проведения вербовки для силовых структур: со скольки до скольки проводится, со скольких рангов можно вербовать сотрудников МО и каковы правила миграции выговоров при вербовке?"
    }
]

PASS_SCORE_PERCENT = 80

# === КОНФИГУРАЦИЯ ТЕЛЕГРАМА ===
TG_TOKEN = 8731457824:AAHpYQiGSHakpMkoVoGFJQNbF3fe_rimxSU
TG_CHAT_ID = 8621189784

async def send_to_telegram(text: str):
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    async with httpx.AsyncClient() as client:
        try:
            await client.post(url, json={"8621189784": 8731457824:AAHpYQiGSHakpMkoVoGFJQNbF3fe_rimxSU, "text": text, "parse_mode": "HTML"})
        except Exception as e:
            print(f"Ошибка отправки в ТГ: {e}")

@app.get("/", response_class=HTMLResponse)
async def get_test_page():
    start_time = time.time()
    fraction_options = "".join([f"<option value='{f}'>{f}</option>" for f in FRACTIONS])

    steps_html = ""
    step_index = 2

    # Тестовые слайды
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
        <div class="step-content animate-slide" id="step-{step_index}" style="display: none;">
            <div class="question-header">ТЕСТОВАЯ ЧАСТЬ • ВОПРОС {step_index - 1} из {len(CHOICE_QUESTIONS) + len(TEXT_QUESTIONS)}</div>
            <p class="question-text">{q['text']}</p>
            <div class="options-container">{options_html}</div>
            <div class="btn-group">
                <button type="button" class="btn btn-secondary" onclick="prevStep({step_index})">Назад</button>
                <button type="button" class="btn btn-primary" onclick="nextStep({step_index})">Далее</button>
            </div>
        </div>
        """
        step_index += 1

    # Письменные слайды
    for q in TEXT_QUESTIONS:
        steps_html += f"""
        <div class="step-content animate-slide" id="step-{step_index}" style="display: none;">
            <div class="question-header">СИТУАЦИОННЫЙ СЕКТОР • ЗАДАНИЕ {step_index - 1}</div>
            <p class="question-text" style="color: #ffaa00;">{q['text']}</p>
            <textarea name="q_{q['id']}" placeholder="Введите развернутый ответ на ситуацию (минимум 30 символов)..." class="text-answer" rows="7"></textarea>
            <div class="btn-group">
                <button type="button" class="btn btn-secondary" onclick="prevStep({step_index})">Назад</button>
                {"<button type='button' class='btn btn-primary' onclick='nextStep(" + str(step_index) + ")'>Далее</button>" if step_index < (len(CHOICE_QUESTIONS) + len(TEXT_QUESTIONS) + 1) else ""}
                {"<button type='submit' class='btn btn-submit'>Зафиксировать протокол в базе</button>" if step_index == (len(CHOICE_QUESTIONS) + len(TEXT_QUESTIONS) + 1) else ""}
            </div>
        </div>
        """
        step_index += 1

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>ТЕРМИНАЛ ПРОВЕРКИ ГОС. СТРУКТУР</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{
                font-family: 'Courier New', Courier, monospace;
                background: #06060a;
                color: #00ff66;
                margin: 0;
                padding: 20px;
                overflow-x: hidden;
            }}
            .terminal-container {{
                max-width: 750px;
                margin: 40px auto;
                background: #0b0c10;
                padding: 40px;
                border-radius: 2px;
                box-shadow: 0 0 30px rgba(255, 69, 0, 0.2);
                border: 2px solid #1f222e;
                position: relative;
            }}
            .terminal-header {{
                text-align: center;
                margin-bottom: 40px;
                border-bottom: 2px dashed #1f222e;
                padding-bottom: 20px;
            }}
            .terminal-title {{
                color: #ff4500;
                margin: 0;
                font-size: 22px;
                text-transform: uppercase;
                letter-spacing: 2px;
            }}
            .input-field, .select-field {{
                width: 100%;
                padding: 14px;
                background: #101116;
                border: 1px solid #2a2e3d;
                border-radius: 4px;
                color: #fff;
                font-size: 16px;
                box-sizing: border-box;
                font-family: inherit;
            }}
            .input-field:focus, .select-field:focus {{
                outline: none;
                border-color: #ff4500;
            }}
            .question-header {{
                color: #ff4500;
                font-size: 13px;
                margin-bottom: 15px;
                letter-spacing: 1px;
            }}
            .question-text {{
                font-size: 17px;
                color: #fff;
                margin-top: 0;
                margin-bottom: 25px;
                line-height: 1.6;
            }}
            .option-card {{
                display: flex;
                align-items: center;
                margin: 12px 0;
                padding: 15px;
                background: #101116;
                border: 1px solid #1f222e;
                border-radius: 4px;
                cursor: pointer;
                color: #c4c9de;
                transition: transform 0.2s;
            }}
            .option-card:hover {{
                border-color: #ff4500;
                background: #14161f;
                transform: translateX(5px);
            }}
            .text-answer {{
                width: 100%;
                background: #101116;
                border: 1px solid #2a2e3d;
                border-radius: 4px;
                color: #fff;
                padding: 15px;
                font-size: 15px;
                box-sizing: border-box;
                font-family: inherit;
                resize: none;
            }}
            .text-answer:focus {{ outline: none; border-color: #ff4500; }}
            .btn-group {{ display: flex; justify-content: space-between; margin-top: 30px; gap: 15px; }}
            .btn {{
                padding: 14px 28px;
                border: none;
                border-radius: 4px;
                font-size: 14px;
                font-weight: bold;
                cursor: pointer;
                text-transform: uppercase;
                font-family: inherit;
            }}
            .btn-primary {{ background: #ff4500; color: #fff; }}
            .btn-secondary {{ background: #1f222e; color: #8a91a8; }}
            .btn-submit {{ background: #00ff66; color: #000; width: 100%; }}
            
            /* КЛЮЧЕВАЯ АНИМАЦИЯ СЛАЙДОВ */
            .animate-slide {{
                animation: fadeInSlide 0.4s ease-in-out forwards;
            }}
            @keyframes fadeInSlide {{
                from {{
                    opacity: 0;
                    transform: translateY(15px);
                }}
                to {{
                    opacity: 1;
                    transform: translateY(0);
                }}
            }}
        </style>
    </head>
    <body>
        <div class="terminal-container">
            <div class="terminal-header">
                <h2 class="terminal-title">▲ СИСТЕМА ПРОВЕРКИ СТАРШЕГО СОСТАВА ▲</h2>
                <p style="color: #6c738c; font-size: 12px; margin: 5px 0 0 0;">БАЗА ДАННЫХ И ПРАВИЛА ГОСУДАРСТВЕННЫХ СТРУКТУР RADMIR</p>
            </div>
            
            <form action="/submit" method="post" id="quiz-form">
                <input type="hidden" name="start_time" value="{start_time}">

                <div class="step-content animate-slide" id="step-1">
                    <div style="margin-bottom: 25px;">
                        <label style="display:block; margin-bottom:10px; color:#ff4500;">> Авторизовать никнейм (Имя_Фамилия):</label>
                        <input type="text" id="nick-input" name="nickname" placeholder="Dmitry_Kabanov" required class="input-field">
                    </div>
                    
                    <div style="margin-bottom: 35px;">
                        <label style="display:block; margin-bottom:10px; color:#ff4500;">> Выберите ведомство:</label>
                        <select id="frac-input" name="fraction" required class="select-field">
                            <option value="" disabled selected>-- ДОСТУПНЫЕ ФРАКЦИИ --</option>
                            {fraction_options}
                        </select>
                    </div>
                    <button type="button" class="btn btn-primary" style="width: 100%;" onclick="startQuiz()">Начать прохождение</button>
                </div>
                
                {steps_html}
            </form>
        </div>

        <script>
            function startQuiz() {{
                const nick = document.getElementById('nick-input').value.trim();
                const frac = document.getElementById('frac-input').value;
                if(!nick || !frac) {{
                    alert("КРИТИЧЕСКАЯ ОШИБКА: Заполните данные авторизации.");
                    return;
                }}
                document.getElementById('step-1').style.display = 'none';
                document.getElementById('step-2').style.display = 'block';
            }}

            function nextStep(currentStep) {{
                const inputs = document.querySelectorAll(`#step-${{currentStep}} input[type="radio"]`);
                if(inputs.length > 0) {{
                    let checked = false;
                    inputs.forEach(i => {{ if(i.checked) checked = true; }});
                    if(!checked) {{
                        alert("ВНИМАНИЕ: Выберите вариант ответа перед переходом.");
                        return;
                    }}
                }}
                
                const textarea = document.querySelector(`#step-${{currentStep}} textarea`);
                if(textarea && textarea.value.trim().length < 30) {{
                    alert("ОШИБКА: Письменный ответ слишком короткий (минимум 30 подробных символов).");
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
    status_text = "🟢 УСПЕШНО (Тест сдан)" if is_passed else "🔴 ПРОВАЛЕН (Недостаточно баллов)"

    # Формируем лог для Telegram
    tg_message = (
        f"<b>📥 ПОСТУПИЛ НОВЫЙ ПРОТОКОЛ ТЕСТА</b>\n"
        f"-------------------------------------\n"
        f"👤 <b>Кандидат:</b> {nickname}\n"
        f"🏢 <b>Фракция:</b> {fraction}\n"
        f"⏱️ <b>Время прохождения:</b> {time_str}\n"
        f"📊 <b>Результат тестов:</b> {correct_count} из {total_choice} ({score_percent}%)\n"
        f"📜 <b>Вердикт:</b> {status_text}\n\n"
        f"<b>📝 ПИСЬМЕННЫЕ ОТВЕТЫ КАНДИДАТА:</b>\n"
    )

    written_html = ""
    for q in TEXT_QUESTIONS:
        ans = form_data.get(f"q_{q['id']}", "Нет ответа")
        # Экранируем спецсимволы HTML для корректного отображения на сайте
        ans_clean = ans.replace("<", "&lt;").replace(">", "&gt;")
        written_html += f"<div style='margin-bottom:15px; padding:10px; background:#101116; border-left:3px solid #ff4500;'><p style='color:#ff4500; margin:0;'><b>{q['text']}</b></p><p style='margin:5px 0 0 0; color:#fff;'><i>Ответ: {ans_clean}</i></p></div>"
        
        # Для Telegram убираем HTML теги из ответов пользователя, чтобы избежать конфликтов форматирования
        tg_ans = ans.replace("<", "").replace(">", "")
        tg_message += f"\n❓ <i>{q['text']}</i>\n✍️ <b>Ответ:</b> {tg_ans}\n"

    # БЕЗОПАСНАЯ ОТПРАВКА В ТЕЛЕГРАМ
    # Даже если токен неверный или упал интернет — сайт НЕ выдаст ошибку 500
    try:
        url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url, json={"chat_id": TG_CHAT_ID, "text": tg_message, "parse_mode": "HTML"})
            if response.status_code != 200:
                print(f"Ошибка API Telegram: {response.text}")
    except Exception as e:
        print(f"Критическая ошибка отправки в ТГ: {e}")

    # Финальная страница (покажется 100%)
    result_html = f"""
    <!DOCTYPE html>
    <html>
    <head><title>ПРОТОКОЛ ОТПРАВЛЕН</title><meta charset="utf-8"></head>
    <body style="font-family: 'Courier New', monospace; background: #06060a; color: #fff; padding: 40px 20px;">
        <div style="max-width: 650px; margin: 40px auto; background: #0b0c10; padding: 40px; border: 2px solid #1f222e;">
            <h2 style="text-align: center; color: #00ff66;">■ ДАННЫЕ УСПЕШНО ЗАПИСАНЫ ■</h2>
            <hr style="border:0; border-top:2px dashed #1f222e; margin:20px 0;">
            <p>Ваш протокол тестирования сформирован и отправлен в базу данных следящего руководства.</p>
            <p><b>Правильных ответов (тесты):</b> {correct_count} из {total_choice} ({score_percent}%)</p>
            <h3 style="color:#ff4500;">Ваши письменные ответы сохранены для ручной проверки:</h3>
            {written_html}
            <p style="text-align:center; color:#6c738c; font-size:12px; margin-top:30px;">Вы можете закрыть эту страницу.</p>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=result_html)
