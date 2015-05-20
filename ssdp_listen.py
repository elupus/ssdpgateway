#!/usr/bin/env python


import socket
import sys
import struct
import select
import udp
import ip
import ssdp_sender

MCAST_GROUPS = ['239.255.255.250', 'FF02::C', 'FF05::C', 'FF08::C', 'FF0E::C']
MCAST_PORTS  = [1900]


def create_socket(addrinfo):
    s = socket.socket(addrinfo[0], addrinfo[1])
    try:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        s.setblocking(0)
        s.bind(addrinfo[4])

        group_bin = socket.inet_pton(addrinfo[0], addrinfo[4][0])


        if addrinfo[0] == socket.AF_INET:
            print 'IPV4'
            mreq = group_bin + struct.pack('=I', socket.INADDR_ANY)
            print mreq
            s.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        elif addrinfo[0] == socket.AF_INET6:
            print 'IPV6'
            mreq = group_bin + struct.pack('@I', 0)
            print mreq
            s.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_JOIN_GROUP, mreq)
        else:
            print 'Unkonwn socket type' + addrinfo[0]
    except Exception as e:
        s.close
        s = None
        raise

    return s

def open_listeners():
    sockets = []
    for group in MCAST_GROUPS:
        for port in MCAST_PORTS:
            addrinfos = socket.getaddrinfo(group, port, 0, socket.SOCK_DGRAM)
            for addrinfo in addrinfos:
                print addrinfo
                try:
                    sockets.append(create_socket(addrinfo))
                except Exception,e:
                    print e
    return sockets

def main():
    sockets = open_listeners()
    sender  = ssdp_sender.SsdpSender()

    while len(sockets):
        sread, swrite, serror = select.select(sockets, [], sockets, 0)
        for s in sread:
            name = s.getsockname()
            data, src = s.recvfrom(4096)
            sender.send(data, s.family, src, s.getsockname())

        for s in serror:
            sockets.remove(s)



if __name__ == '__main__':
    main()


