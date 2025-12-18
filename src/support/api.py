from ninja import Router

router = Router()


# Пример эндпоинта для теста
@router.get("/ping")
def ping(request):
    return {"ping": "pong"}
