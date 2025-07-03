from enum import Enum, auto

class Step(Enum):
    WAITING_MODEL   = auto()   # ждём фото модели
    WAITING_GARMENT = auto()   # ждём фото одежды
    PROCESSING      = auto()   # FASHN работает