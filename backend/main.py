from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from celery.result import AsyncResult
from tasks import detect_cells
import uuid

# Создаём приложение FastAPI
app = FastAPI(
    title="Blood Cell Counter API",
    description="API для подсчета клеток крови с помощью YOLOv8",
    version="1.0.0"
)

# Разрешаем запросы с любого адреса (нужно чтобы Streamlit мог обращаться к API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    """Проверка что сервер работает"""
    return {"status": "ok", "message": "Blood Cell Counter API"}

@app.post("/detect")
async def detect(
    file: UploadFile = File(...),       # картинка от пользователя
    model_type: str = "nano"            # "nano" = быстрая, "medium" = точная
):
    """
    Принимает картинку и кладёт задачу в очередь.
    Сразу возвращает task_id — по нему потом узнаем результат.
    """
    # Проверяем что загрузили картинку а не pdf или что-то другое
    if file.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(
            status_code=400,
            detail="Только JPEG и PNG файлы"
        )

    # Проверяем что выбрана правильная модель
    if model_type not in ["nano", "medium"]:
        raise HTTPException(
            status_code=400,
            detail="model_type должен быть 'nano' или 'medium'"
        )

    # Читаем байты картинки
    image_bytes = await file.read()

    # Кладём задачу в очередь Celery и сразу получаем id задачи
    task = detect_cells.delay(image_bytes, model_type)

    # Возвращаем id — frontend будет опрашивать по нему
    return {
        "task_id": task.id,
        "status": "queued"
    }

@app.get("/result/{task_id}")
def get_result(task_id: str):
    """
    Frontend спрашивает: готов ли результат?
    Возвращаем статус или готовый результат.
    """
    task = AsyncResult(task_id)

    if task.state == "PENDING":
        return {"status": "processing"}

    if task.state == "FAILURE":
        return {"status": "error", "detail": str(task.info)}

    if task.state == "SUCCESS":
        return {
            "status": "done",
            "result": task.result
        }

    return {"status": task.state}