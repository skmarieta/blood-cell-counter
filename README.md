# 🔬 Blood Cell Counter

MVP веб-приложение для автоматического подсчёта клеток крови на основе YOLOv8.

## Классы объектов
- 🔴 **RBC** — эритроциты
- 🔵 **WBC** — лейкоциты  
- 🟣 **Platelets** — тромбоциты

## Технологии
- **ML**: YOLOv8n (быстрая) и YOLOv8m (точная)
- **Backend**: FastAPI + Celery + Redis
- **Frontend**: Streamlit

## Результаты моделей

| Модель | mAP50 | mAP50-95 | Скорость |
|--------|-------|----------|----------|
| YOLOv8n (tuned) | 0.913 | 0.626 | 1.6ms |
| YOLOv8m (tuned) | 0.924 | 0.634 | 15.0ms |

## Датасет
[BCCD Dataset](https://www.kaggle.com/datasets/orvile/bccd-blood-cell-count-and-detection-dataset) — 364 изображения, 3 класса.

## Запуск локально

### Требования
- Docker и Docker Compose
- Веса моделей в папке `models/`

### Запуск backend
```bash
docker-compose up
```

### Запуск frontend
```bash
cd frontend
pip install -r requirements.txt
streamlit run app.py
```

## Структура проекта
```
blood-cell-counter/
├── models/          # веса YOLOv8 моделей
├── backend/         # FastAPI + Celery
├── frontend/        # Streamlit приложение
└── notebooks/       # Colab ноутбук с обучением
```