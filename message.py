import json
import copy


# TODO: TRANSFORMAR ESSA CLASSE EM CLASSE MAE
class Handler:
    def __init__(self,payload,header,)

    HEADER = {
        "checksum": "",
        "type": 0,
        "nsequence": 0,
        "size": 0
    }

    MAX_PAYLOAD_SIZE = 512

    @staticmethod
    def get_header(type):
        header = copy.deepcopy(Handler.HEADER)
        header["type"] = type
        return header

    @staticmethod
    def deserialize(msgbytes):
        data = json.loads(msgbytes.decode())
        # TODO: alterar a forma de serialização - mudar de json para struct -
        #  TODO: struct  -  consultar - http://www.bitforestinfo.com/2017/12/code-to-create-tcp-packet-header-with-python-socket-module.html
        # TODO: VALIDAR CHECKSUM -- SE CHECKSUM ERRADO --- IGNORAR MESSAGEM E RAISE EXCEPTION
        if data['header']['type'] == ConnectionMessage.TYPE:
            msg = ConnectionMessage()
            msg.set_message(data)
            return msg
        elif data['header']['type'] == AckClientMessage.TYPE:
            msg = AckClientMessage()
            msg.set_message(data)
            return msg
        elif data['header']['type'] == DataMessage.TYPE:
            size = data["header"]["size"]
            sequence = data["header"]["nsequence"]
            payload = data["payload"]
            msg = DataMessage(payload, size, sequence)
            msg.set_message(data)
            return msg
        elif data['header']['type'] == TotalSegMessage.TYPE:
            msg = TotalSegMessage()
            msg.set_message(data)
            return msg
        elif data['header']['type'] == MissingMessage.TYPE:
            msg = MissingMessage()
            msg.set_message(data)
            return msg
        elif data['header']['type'] == FinMessage.TYPE:
            msg = FinMessage()
            msg.set_message(data)
            return msg

    @staticmethod
    def serialize(msg):
        # TODO: DEFINIR CHECKSUM
        msgbytes = json.dumps(msg.get_message()).encode()
        return msgbytes


#TODO: herdam da classe mãe; colocar os atributos como privados;
#TODO: definir os métodos necessários para não aceder diretamente aos atributos

# primeira mensagem cliente -> servidor (1)
class ConnectionMessage:

    TYPE = 1

    def __init__(self, username="", password="", action="", filename=""):
        self.message =\
        {
            "header": Handler.get_header(ConnectionMessage.TYPE),
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

    def set_message(self, data):
        self.message = data

    def get_username(self):
        return self.message["payload"]["username"]

    def get_password(self):
        return self.message["payload"]["password"]

    def get_action(self):
        return self.message["payload"]["action"]

    def get_filename(self):
        return self.message["payload"]["filename"]

    def get_type(self):
        return self.TYPE

    def __str__(self):
        value = "ConnectionMessage " + str(self.message)
        return value


# mensagem cliente -> servidor (recebeu numero de segmentos) (2)
class AckClientMessage:

    TYPE = 2

    def __init__(self):
        self.message =\
        {
            "header": Handler.get_header(AckClientMessage.TYPE)
        }

    def get_message(self):
        return self.message

    def set_message(self, data):
        self.message = data

    def get_type(self):
        return self.TYPE

    def __str__(self):
        value = "AckClientMessage " + str(self.message)
        return value


# mensagens servidor -> cliente com dados (3)
class DataMessage:

    TYPE = 3

    def __init__(self, payload, size, sequence):
        self.message =\
        {
            "header": Handler.get_header(DataMessage.TYPE),
            "payload": payload
        }
        self.message["header"]["size"] = size
        self.message["header"]["nsequence"] = sequence

    def get_message(self):
        return self.message

    def set_message(self, data):
        self.message = data

    def get_type(self):
        return self.TYPE

    def __str__(self):
        value = "DataMessage " + str(self.message)
        return value


# primeira mensagem servidor -> cliente (4)
class TotalSegMessage:

    TYPE = 4

    def __init__(self):
        self.message =\
        {
            "header": Handler.get_header(TotalSegMessage.TYPE),
            "payload":
            {
                "totalSegments": 0
            }
        }

    def set_total_segments(self, total_segments):
        self.message["payload"]["totalSegments"] = total_segments

    def get_total_segments(self):
        return self.message["payload"]["totalSegments"]

    def get_message(self):
        return self.message

    def set_message(self, data):
        self.message = data

    def get_type(self):
        return self.TYPE

    def __str__(self):
        value = "TotalSegMessage " + str(self.message)
        return value


# mensagem cliente -> servidor (missing) (5)
class MissingMessage:

    TYPE = 5

    def __init__(self):
        self.message = \
            {
                "header": Handler.get_header(MissingMessage.TYPE),
                "payload":
                    {
                        "missing": {}
                    }
            }

    def get_message(self):
        return self.message

    def set_message(self, data):
        self.message = data

    def get_type(self):
        return self.TYPE

    def set_missing(self, lista):
        self.message["payload"]["missing"] = lista


    def __str__(self):
        value = "MissingMessage " + str(self.message)
        return value


# utima mensagem cliente -> servidor (6)
class FinMessage:

    TYPE = 6

    def __init__(self):
        self.message =\
        {
            "header": Handler.get_header(FinMessage.TYPE)
        }

    def get_message(self):
        return self.message

    def set_message(self, data):
        self.message = data

    def get_type(self):
        return self.TYPE

    def __str__(self):
        value = "FinMessage " + str(self.message)
        return value


 def makeDataMessage(nsequence, size, checksum, )