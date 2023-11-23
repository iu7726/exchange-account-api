from django.apps import AppConfig
from util.rabbitmq import RabbitMQManager
import os

class AccountConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'account'

    def ready(self):
        if os.environ.get('RUN_MAIN', None) != 'true':
            # This code will only run once, not twice
            # Put your initialization logic here
            RabbitMQManager()
            pass
