import os
import logging
import requests
import pandas as pd
from io import BytesIO
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# Настраиваем логирование
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.FileHandler("bot.log", encoding="utf-8"), logging.StreamHandler()]
)

def download_and_generate_schedule(group_name):
    today = datetime.now()
    day_of_week = today.weekday()
    logging.info(f"Генерация расписания для группы {group_name}...")

    if day_of_week == 5:  # Суббота
        target_day = today + timedelta(days=2)
    elif day_of_week == 6:  # Воскресенье
        target_day = today + timedelta(days=1)
    else:
        target_day = today

    day_month = int(target_day.strftime("%d%m"))
    url = f"https://altask.ru/images/raspisanie/DO/{day_month}.xls"

    try:
        response = requests.get(url)
        response.raise_for_status()
        file_content = response.content
        file = BytesIO(file_content)
    except Exception as e:
        logging.error(f"Ошибка при загрузке файла расписания: {e}")
        return None

    try:
        if url.endswith('.xls'):
            xlsx = pd.ExcelFile(file, engine="xlrd")
        elif url.endswith('.xlsx'):
            xlsx = pd.ExcelFile(file, engine="openpyxl")
        else:
            raise ValueError("Формат файла не поддерживается")
    except Exception as e:
        logging.error(f"Ошибка при открытии файла расписания: {e}")
        return None

    found = False
    values = []

    for sheet_name in xlsx.sheet_names:
        df = xlsx.parse(sheet_name)
        for row_idx, row in df.iterrows():
            for col_idx, cell in enumerate(row):
                if str(cell).strip() == group_name:
                    found = True
                    start_row = row_idx
                    column = df.columns[col_idx]
                    values = df[column].iloc[start_row:start_row + 13].tolist()
                    break
            if found:
                break
        if found:
            break

    if not found:
        logging.warning(f"Группа {group_name} не найдена в файле расписания.")
        return None

    schedule = [val if pd.notna(val) else "" for val in values]

    df_schedule = pd.DataFrame(schedule, columns=["Расписание"])
    fig, ax = plt.subplots(figsize=(7, len(schedule) * 0.3))
    ax.axis('tight')
    ax.axis('off')
    table = ax.table(cellText=df_schedule.values, colLabels=df_schedule.columns, cellLoc='center', loc='center')

    table.auto_set_font_size(False)
    table.set_fontsize(10)
    for key, cell in table.get_celld().items():
        cell.set_height(0.3)
        cell.set_width(0.6)

    output_path = os.path.abspath("schedule.png")
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)

    logging.info(f"Расписание для {group_name} сохранено в {output_path}.")
    return output_path
