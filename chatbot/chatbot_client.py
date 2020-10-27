from multiprocessing.connection import Client

from .ai_chatbot import Chatbot


class ChatbotClient:
    def __init__(self):
        self._client = Client(address = ('localhost', 6000), authkey = 'aidelcharbot')

        chatbot = Chatbot(port = '')
        chatbot.setDaemon(True)
        chatbot.start()

    def send(self, msg):
        self._client.send(msg)

    def close(self):
        self.send('close')
        self._client.close()