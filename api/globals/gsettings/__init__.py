import settings as mod

class Settings(object):
    def __init__(self):
        for setting in dir(mod):
            if setting == setting.upper():
                setting_value = getattr(mod, setting)
                setattr(self, setting, setting_value)

settings = Settings()

