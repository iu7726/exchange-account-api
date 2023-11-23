import pika, os, json, ssl

class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]

class RabbitMQManager():
    def __init__(self):
        if os.getenv('API_ENV') == 'prod' or os.getenv('API_ENV') == 'production': 
            context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
            self.connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=str(os.getenv('MQ_HOST')),
                    port=int(os.getenv('MQ_PORT')),
                    credentials=pika.PlainCredentials(username=str(os.getenv('MQ_ID')), password=str(os.getenv('MQ_PW'))),
                    ssl_options=pika.SSLOptions(context)
                )
            )
            self.channel = self.connection.channel()
        else:
            self.connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=str(os.getenv('MQ_HOST')),
                    port=int(os.getenv('MQ_PORT')),
                    credentials=pika.PlainCredentials(username=str(os.getenv('MQ_ID')), password=str(os.getenv('MQ_PW')))
                )
            )
            self.channel = self.connection.channel()

    def send_message(self, message, route, exchange):
        try:
            self.channel.basic_publish(exchange=exchange,
                                    routing_key=route,
                                    body=message)
            print(f" [x] Sent '{message}'")
        except pika.exceptions.ConnectionClosed:
            # Handle connection loss and attempt to reconnect
            self.__init__()  # Reinitialize connection and channel
            self.send_message(message, route, exchange)

    def close_connection(self):
        self.connection.close()

def send_mq(message, route, exchange=str(os.getenv('MQ_EXCHANGE'))):
    mq = RabbitMQManager()
    try:
        mq.send_message(json.dumps(message), route, exchange)

        return True
    except pika.exceptions.ConnectionClosed:
        # Handle connection loss and attempt to reconnect
        mq.__init__()  # Reinitialize connection and channel
        mq.send_message(message, route, exchange)
    
    mq.close_connection()
