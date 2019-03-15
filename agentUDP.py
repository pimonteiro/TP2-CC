PDU = 548 # Pode ser mudado, aliás, deve ser mudado!


def sendPacket(data,sock,data_size):
    packets = ["%s"%data[i:i+data_size] for i in range(0,len(data),data_size)]
    packets[-1] = packets[-1] + "\x00"*(len(data)%data_size)
    for p in packets:
        sock.sendto(p,*ADDRINFO)