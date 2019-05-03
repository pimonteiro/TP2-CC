import json
import struct


class Header:
    def __init__(self, che, ty, nseq, siz):
        self.checksum = che
        self.type = ty
        self.nsequence = nseq
        self.size = siz

    def getType(self):
        return self.type

    def getSize(self):
        return self.size

    def getSequence(self):
        return self.nsequence

    def classToBinary(self):
        head = struct.pack('LHLc',self.checksum,self.size,self.nsequence,self.type)
        return head

    def binaryToClass(self, head):
        self.checksum, self.size, self.nsequence, self.type = struct.unpack('LHLc', head)

    def setDataMessageHeader(self, ch, nseq, si):
        self.checksum = ch
        self.type = Message.TYPE_DAT
        self.nsequence = nseq
        self.size = si


class Message:
    HEADER_SIZE = 58
    HEADER_LENGTH = 25

    TYPE_SYN = 1
    TYPE_ACK = 2
    TYPE_DAT = 3
    TYPE_TSG = 4
    TYPE_MMS = 5
    TYPE_FIN = 6
    TYPE_ATE = 7
    TYPE_FNF = 8

    def __init__(self):
        self.header = Header(0,0,0,0)
        self.data = ""

    def getType(self):
        return self.header.getType()

    def getSequence(self):
        return self.header.getSequence()

    def getData(self):
        return self.data

    def classToBinary(self):
        head = self.header.classToBinary()
        if self.header.getType() == Message.TYPE_ACK or self.header.getType() == Message.TYPE_MMS:
            data = json.dumps(self.data).encode()
        else:
            data = self.data.encode()
        return head + data

    def binaryToClass(self, mbytes):
        self.header.binaryToClass(mbytes[:Message.HEADER_LENGTH])
        self.data = struct.unpack("utf-8", mbytes[Message.HEADER_LENGTH:Message.HEADER_SIZE])

    # primeira mensagem cliente -> servidor (1)
    def makeConnectionMessage(self, username, password, action, filename):
        data = {
            "username": username,
            "password": password,
            "action": action,
            "filename": filename
        }
        che = Message.calculate_checksum(json.dumps(data))
        self.header = Header(che, Message.TYPE_SYN, 0, data.__sizeof__())
        self.data = data

    # mensagem cliente -> servidor (recebeu numero de segmentos) (2)
    def makeMessage(self, data, type):
        che = 0 # TODO Funcao de calcular checksum
        self.header = Header(che, type, 0, data.__sizeof__())
        self.data = data

    # mensagem cliente -> servidor (missing) (5)
    def makeMissingMessage(self, miss):
        data = {
            'data': miss
        }
        che = Message.calculate_checksum(json.dumps(data))
        self.header = Header(che, Message.TYPE_MMS, 0, data.size())

    def makeTotalSegMessage(self, total, port):
        data = {
            "data": total,
            "port": port
        }
        che = Message.calculate_checksum(json.dumps(data))
        self.header = Header(che, Message.TYPE_TSG, 0, data.__sizeof__())

    def calculate_checksum(msg):
        assert isinstance(msg, str)
        ordinalSum = sum(ord(x) for x in msg)
        return ordinalSum