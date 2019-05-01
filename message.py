import json


class Handler:

    @staticmethod
    def deserialize(msgbytes):
        data = json.loads(msgbytes.decode())
        if data['header']['type'] == ConnectionMessage.TYPE:
            msg = ConnectionMessage()
            msg.message = data
            return msg
        elif data['header']['type'] == AckClientMessage.TYPE:
            msg = AckClientMessage()
            msg.message = data
            return msg
        elif data['header']['type'] == DataMessage.TYPE:
            msg = DataMessage()
            msg.message = data
            return msg
        elif data['header']['type'] == TotalSegMessage.TYPE:
            msg = TotalSegMessage()
            msg.message = data
            return msg
        elif data['header']['type'] == MissingMessage.TYPE:
            msg = MissingMessage()
            msg.message = data
            return msg
        elif data['header']['type'] == FinMessage.TYPE:
            msg = FinMessage()
            msg.message = data
            return msg

    @staticmethod
    def serialize(msg):
        msgbytes = json.dumps(msg.get_message()).encode()
        return msgbytes


# primeira mensagem cliente -> servidor (1)
class ConnectionMessage:

    TYPE = 1

    def __init__(self, username="", password="", action="", filename=""):
        self.message =\
        {
            "header":
            {
                "checksum": "",
                "type": ConnectionMessage.TYPE,
                "nsequence": "",
                "size": "" #(cabeçalho + payload)
            },
            "payload":
            {
                "username": username,
                "password": password,
                "action": action,
                "filename": filename
            }
        }

    def get_message(self):
        return self.message


# mensagem cliente -> servidor (recebeu numero de segmentos) (2)
class AckClientMessage:

    TYPE = 2

    def __init__(self):
        self.message =\
        {
            "header":
            {
                "checksum": "",
                "type": AckClientMessage.TYPE,
                "nsequence": "",
                "size": "" #(cabeçalho + payload)
            },
        }

    def get_message(self):
        return self.message


# mensagens servidor -> cliente com dados (3)
class DataMessage:

    TYPE = 3

    def __init__(self):
        self.message =\
        {
            "header":
                {
                    "checksum": "",
                    "type": DataMessage.TYPE,  #no caso do ultimo segmento vai um FIN
                    "nsequence": "",
                    "size": ""  # (cabeçalho + payload)
                },
            "payload": "data"
        }

    def get_message(self):
        return self.message


# primeira mensagem servidor -> cliente (4)
class TotalSegMessage:

    TYPE = 4

    def __init__(self):
        self.message =\
        {
            "header":
                {
                    "checksum": "",
                    "type": TotalSegMessage.TYPE,
                    "nsequence": "",
                    "size": ""  # (cabeçalho + payload)
                },
            "payload":
            {
                "totalSegments": ""
            }
        }

    def get_message(self):
        return self.message


# mensagem cliente -> servidor (missing) (5)
class MissingMessage:

    TYPE = 5

    def __init__(self):
        self.message = \
            {
                "header":
                    {
                        "checksum": "",
                        "type": MissingMessage.TYPE,
                        "nsequence": "",
                        "size": ""  # (cabeçalho + payload)
                    },
                "payload":
                    {
                        "missing": []
                    }
            }

    def get_message(self):
        return self.message


# utima mensagem cliente -> servidor (6)
class FinMessage:

    TYPE = 6

    def __init__(self):
        self.message =\
        {
            "header":
            {
                "checksum": "",
                "type": FinMessage.TYPE,
                "nsequence": "",
                "size": "" #(cabeçalho + payload)
            },
        }

    def get_message(self):
        return self.message
