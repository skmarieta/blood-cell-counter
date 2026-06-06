import streamlit as st
from ultralytics import YOLO
from PIL import Image
import io
import base64

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
    st.image(uploaded_file, caption="Загруженное изображение", use_column_width=True)

    if st.button("🔍 Определить клетки", type="primary"):
        with st.spinner("Модель анализирует изображение..."):
            # Загружаем модель
            model_path = f"models/yolov8{'n' if model_type == 'nano' else 'm'}.pt"
            model = YOLO(model_path)

            # Читаем картинку
            image = Image.open(uploaded_file).convert("RGB")

            # Запускаем детекцию
            results = model(image)

            # Считаем клетки
            counts = {"RBC": 0, "WBC": 0, "Platelets": 0}
            class_names = {0: "RBC", 1: "WBC", 2: "Platelets"}

            for box in results[0].boxes:
                class_id = int(box.cls[0])
                counts[class_names[class_id]] += 1

        st.success("✅ Анализ завершён!")
        st.divider()

        # Счётчики
        st.subheader("Результаты подсчёта")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("🔴 RBC", counts["RBC"], help="Эритроциты")
        col2.metric("🔵 WBC", counts["WBC"], help="Лейкоциты")
        col3.metric("🟣 Platelets", counts["Platelets"], help="Тромбоциты")
        col4.metric("📊 Всего", sum(counts.values()))

        # Картинка с рамками
        st.subheader("Визуализация детекции")
        result_image = results[0].plot()
        st.image(result_image, caption="Результат детекции", use_column_width=True)

        st.caption(f"Использована модель: YOLOv8{'n' if model_type == 'nano' else 'm'}")