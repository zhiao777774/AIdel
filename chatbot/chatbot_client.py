from .ai_chatbot import Chatbot


class ChatbotClient:
    def __init__(self, port):
        self._chatbot = Chatbot(port)
        self._chatbot.setDaemon(True)
        self._chatbot.start()

    def send(self, msg):
        self._chatbot.act(msg)

    def close(self):
        self.send('close')