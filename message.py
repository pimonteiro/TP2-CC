import json
import struct
import sys


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

    def getAll(self):
        return self.checksum, self.type, self.nsequence, self.size

    def getChecksum(self):
        return self.checksum
    def classToBinary(self):
        head = struct.pack('LHLc', self.checksum, self.size, self.nsequence, self.type.encode())
        return head

    def binaryToClass(self, head):
        self.checksum, self.size, self.nsequence, self.type = struct.unpack('LHLc', head)
        self.type = self.type.decode('utf-8')

    def setDataMessageHeader(self, ch, nseq, si):
        self.checksum = ch
        self.type = Message.TYPE_DAT
        self.nsequence = nseq
        self.size = si

    def __str__(self):
        value = \
            {
                "checksum": self.checksum,
                "type": self.type,
                "nsequence": self.nsequence,
                "size": self.size
            }

        return "header: " + str(value)


class Message:
    HEADER_SIZE = 58
    HEADER_LENGTH = struct.calcsize("LHLc")

    TYPE_SYN = "1"
    TYPE_ACK = "2"
    TYPE_DAT = "3"
    TYPE_TSG = "4"
    TYPE_MMS = "5"
    TYPE_FIN = "6"
    TYPE_ATE = "7"
    TYPE_FNF = "8"
    TYPE_COR = "9"

    def __init__(self):
        self.header = Header(0, 0, 0, 0)
        self.data = ""

    def getType(self):
        return self.header.getType()

    def getSequence(self):
        return self.header.getSequence()

    def getData(self):
        return self.data

    def getHeader(self):
        return self.header.getAll()

    def getChecksum(self):
        return self.header.getChecksum()

    def classToBinary(self):
        head = self.header.classToBinary()
        if self.header.getType() in (Message.TYPE_MMS, Message.TYPE_SYN, Message.TYPE_TSG):
            data = json.dumps(self.data).encode()

        else:
            if isinstance(self.data, str):
                data = self.data.encode()
            else:
                data = self.data

        return head + data

    def binaryToClass(self, mbytes):
        self.header.binaryToClass(mbytes[:Message.HEADER_LENGTH])

        if self.header.getType() in (Message.TYPE_MMS, Message.TYPE_SYN, Message.TYPE_TSG):
            self.data = json.loads(mbytes[Message.HEADER_LENGTH:].decode('utf-8'))

        elif self.header.getType() in (Message.TYPE_ATE, Message.TYPE_FNF):
            self.data = mbytes[Message.HEADER_LENGTH:].decode('utf-8')

        else:
            self.data = mbytes[Message.HEADER_LENGTH:]


    # primeira mensagem cliente -> servidor (1)
    def makeConnectionMessage(self, username, password, action, filename, my_server_port):
        data = {
            "username": username,
            "password": password,
            "action": action,
            "filename": filename,
            "my_server_port": my_server_port
        }
        che = Message.calculate_checksum(json.dumps(data))
        self.header = Header(che, Message.TYPE_SYN, 0, sys.getsizeof(data))
        self.data = data

    # mensagem cliente -> servidor (recebeu numero de segmentos) (2)
    def makeMessage(self, data, type, nseq):
        che = Message.calculate_checksum(data)
        self.header = Header(che, type, nseq, sys.getsizeof(data))
        self.data = data

    # mensagem cliente -> servidor (missing) (5)
    def makeMissingMessage(self, miss):

        data = {
            'data': list(miss)[20]
        }
        che = Message.calculate_checksum(json.dumps(data))
        self.header = Header(che, Message.TYPE_MMS, 0, sys.getsizeof(data))
        self.data = data

    def makeTotalSegMessage(self, total, port):
        data = {
            "data": total,
            "port": port
        }
        che = Message.calculate_checksum(json.dumps(data))
        self.header = Header(che, Message.TYPE_TSG, 0, sys.getsizeof(data))
        self.data = data

    @staticmethod
    def calculate_checksum(msg):
        assert isinstance(msg, (bytes, str))
        if isinstance(msg, str):
            ordinalSum = sum(ord(x) for x in msg)
            return ordinalSum
        else:
            ordinalSum = sum(x for x in msg)
            return ordinalSum

    def __str__(self):
        value = \
            {
                "header": str(self.header),
                "data": str(self.data)
            }

        return "message: " + str(value)

    def verifyIntegrity(self):
        dat = self.data
        if isinstance(self.data, dict):
            dat = json.dumps(self.data)
        orig = self.getChecksum()
        givn = Message.calculate_checksum(dat)

        if (orig == givn):
            return True
        else:
            return False