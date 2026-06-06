import streamlit as st
import requests
import base64
import time
from PIL import Image
import io

# Адрес нашего backend
BACKEND_URL = "http://localhost:8000"

# Настройка страницы
st.set_page_config(
    page_title="Blood Cell Counter",
    page_icon="🔬",
    layout="centered"
)

st.title("🔬 Blood Cell Counter")
st.markdown("Автоматический подсчёт клеток крови с помощью YOLOv8")

# Выбор модели
st.subheader("Выбор модели")
model_type = st.radio(
    "Какую модель использовать?",
    options=["nano", "medium"],
    format_func=lambda x: "⚡ Быстрая (YOLOv8n)" if x == "nano" else "🎯 Точная (YOLOv8m)",
    horizontal=True
)

st.divider()

# Загрузка картинки
st.subheader("Загрузка изображения")
uploaded_file = st.file_uploader(
    "Загрузите снимок крови",
    type=["jpg", "jpeg", "png"]
)

if uploaded_file is not None:
    # Показываем загруженную картинку
    st.image(uploaded_file, caption="Загруженное изображение", use_column_width=True)

    # Кнопка запуска детекции
    if st.button("🔍 Определить клетки", type="primary"):

        # Отправляем картинку на backend
        with st.spinner("Отправляем задачу в очередь..."):
            response = requests.post(
                f"{BACKEND_URL}/detect",
                files={"file": uploaded_file.getvalue()},
                params={"model_type": model_type}
            )

            if response.status_code != 200:
                st.error(f"Ошибка: {response.text}")
                st.stop()

            task_id = response.json()["task_id"]

        # Ждём результата — опрашиваем каждые 2 секунды
        with st.spinner("Модель анализирует изображение..."):
            while True:
                result_response = requests.get(
                    f"{BACKEND_URL}/result/{task_id}"
                )
                result = result_response.json()

                if result["status"] == "done":
                    break
                elif result["statu