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
        self.header = ""
        self.data = ""

    def classToBinary(self):
        head = self.header.classToBinary()
        if self.header.getType() == Message.TYPE_ACK || self.header.getType() == Message.TYPE_MMS:
            data = json.dumps(self.data).encode()
        else:
            data = self.data.encode()
        return head + data


    # primeira mensagem cliente -> servidor (1)
    @staticmethod
    def makeConnectionMessage(self, username, password, action, filename):
        data = {
            "username": username,
            "password": password,
            "action": action,
            "filename": filename
        }
        che = 0 # TODO Funcao de calcular checksum
        self.header = Header(che, Message.TYPE_SYN, 0, data.__sizeof__())
        self.data = data

    # mensagem cliente -> servidor (recebeu numero de segmentos) (2)
    def makeMessage(self, data, type):
        che = 0 # TODO Funcao de calcular checksum
        self.header = Header(che, type, 0, data.size())
        self.data = data

    # mensagem cliente -> servidor (missing) (5)
    def makeMissing_TotalSegMessage(self, miss):
        che = 0
        self.header = Header(che, Message.TYPE_MMS, 0, miss.size())
