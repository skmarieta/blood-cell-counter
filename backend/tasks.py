import io
import os
from celery import Celery
from PIL import Image
from ultralytics import YOLO
import base64

# Подключаемся к Redis — он хранит очередь задач
# Redis работает локально на стандартном порту 6379
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Создаём приложение Celery
# "worker" — название приложения
# broker — откуда берём задачи (Redis)
# backend — куда кладём результаты (тоже Redis)
celery_app = Celery(
    "worker",
    broker=REDIS_URL,
    backend=REDIS_URL
)

# Пути к моделям
MODELS = {
    "nano":   os.path.join(os.path.dirname(__file__), "..", "models", "yolov8n.pt"),
    "medium": os.path.join(os.path.dirname(__file__), "..", "models", "yolov8m.pt"),
}

# Загружаем модели один раз при старте — не при каждом запросе
# Это экономит время: загрузка модели занимает ~1 секунду
_loaded_models = {}

def get_model(model_type: str) -> YOLO:
    """Возвращает загруженную модель. Загружает если ещё не загружена."""
    if model_type not in _loaded_models:
        _loaded_models[model_type] = YOLO(MODELS[model_type])
    return _loaded_models[model_type]


@celery_app.task
def detect_cells(image_bytes: bytes, model_type: str) -> dict:
    """
    Главная задача — принимает байты картинки, запускает детекцию,
    возвращает результат с количеством клеток и картинкой с рамками.
    """
    # Превращаем байты обратно в картинку
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

    # Берём нужную модель
    model = get_model(model_type)

    # Запускаем детекцию
    results = model(image)

    # Считаем количество каждого класса
    counts = {"RBC": 0, "WBC": 0, "Platelets": 0}
    class_names = {0: "RBC", 1: "WBC", 2: "Platelets"}

    for box in results[0].boxes:
        class_id = int(box.cls[0])
        class_name = class_names[class_id]
        counts[class_name] += 1

    # Рисуем рамки на картинке и конвертируем в base64
    # base64 — способ передать картинку как текст через JSON
    result_image = results[0].plot()  # numpy array с нарисованными рамками
    pil_image = Image.fromarray(result_image)

    buffer = io.BytesIO()
    pil_image.save(buffer, format="JPEG")
    image_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

    return {
        "counts": counts,
        "total": sum(counts.values()),
        "model_used": model_type,
        "image_base64": image_base64
    }