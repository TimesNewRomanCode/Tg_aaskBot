import os
import requests
import pandas as pd
from io import BytesIO
import matplotlib.pyplot as plt
from datetime import datetime, timedelta


def download_and_generate_schedule(group_name):
    today = datetime.now()
    day_of_week = today.weekday()


    if day_of_week == 5:  # Суббота
        target_day = today + timedelta(days=2)
    elif day_of_week == 6:  # Воскресенье
        target_day = today + timedelta(days=1)
    else:
        target_day = today + timedelta(days=1)

    day_month = int(target_day.strftime("%d%m"))

    url = f"https://altask.ru/images/raspisanie/DO/{day_month}.xls"
    response = requests.get(url)
    file_content = response.content
    file = BytesIO(file_content)

    if url.endswith('.xls'):
        xlsx = pd.ExcelFile(file, engine="xlrd")
    elif url.endswith('.xlsx'):
        xlsx = pd.ExcelFile(file, engine="openpyxl")
    else:
        raise ValueError("Формат файла не поддерживается")

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

    schedule = [val if pd.notna(val) else "" for val in values]

    if day_of_week == 6:
        merged_schedule = [schedule[0]]
        merged_schedule.append(schedule[1])
        merged_schedule.append(f"{schedule[2]}\n{schedule[3]}")
        merged_schedule.append(f"{schedule[4]}\n{schedule[5]}")
        merged_schedule.append(schedule[6])
        merged_schedule.append(f"{schedule[7]}\n{schedule[8]}")
        merged_schedule.append(f"{schedule[9]}\n{schedule[10]}")
        merged_schedule.append(f"{schedule[11]}\n{schedule[12]}")
    else:
        merged_schedule = [schedule[0]]
        for i in range(1, len(schedule) - 1, 2):
            merged_schedule.append(
                f"{schedule[i]}\n{schedule[i + 1]}" if schedule[i] and schedule[i + 1] else schedule[i])

    # Создаем таблицу
    df_schedule = pd.DataFrame(merged_schedule, columns=["Расписание"])

    fig, ax = plt.subplots(figsize=(7, len(merged_schedule) * 0.3))
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

    return output_path
