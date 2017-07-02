class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            class_obj = super(Singleton, cls).__call__(*args, **kwargs)
            cls._instances[cls] = class_obj

        return cls._instances[cls]
