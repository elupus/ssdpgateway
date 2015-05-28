#!/usr/bin/env python

import socket
import sys
import struct
import select
import ip
import udp
import rpyc

def repack(data, fmt, offset):
    val  = struct.unpack_from("!" + fmt, data, offset)
    struct.pack_into("" + fmt, data, offset, val[0])

class SsdpSender():
    def __init__(self):
        
        self.socket_v4 = socket.socket(socket.AF_INET,
                                       socket.SOCK_RAW,
                                       socket.IPPROTO_IP)
        self.socket_v4.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
        self.socket_v4.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 0)

        #self.socket_v6 = socket.socket(socket.AF_INET6,
        #                               socket.SOCK_RAW,
        #                               socket.IPPROTO_IP)
        #self.socket_v6.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

    def send(self, data, family, src, dst):
        packet_udp       = udp.Packet()
        packet_udp.sport = src[1]
        packet_udp.dport = dst[1]
        packet_udp.data  = data

        packet_ip        = ip.Packet()
        packet_ip.src    = src[0]
        packet_ip.dst    = dst[0]
        packet_ip.ttl    = 1
        packet_ip.p      = 17
        packet_ip.data   = udp.assemble(packet_udp, 0)

        packet = bytearray(ip.assemble(packet_ip))

        #Restore byte order for OSX
        repack(packet, "H", 2)
        repack(packet, "H", 6)

        print ':'.join('{:02x}'.format(c) for c in packet)
        if   family == socket.AF_INET:
            self.socket_v4.sendto(packet, dst)
        #elif family == socket.AF_INET6:
        #    self.socket_v6.sendto(packet, dst)
        else:
            raise "Socket family not implemented"

def test():
    sender = SsdpSender()
    sender.send('', socket.AF_INET, ('192.168.4.1', 9999), ('239.255.255.250', 1900))
    sender.send2('', socket.AF_INET, ('192.168.4.1', 9999), ('239.255.255.250', 1900))
    return

def server():
    class SsdpSenderService(rpyc.Service):
        from ssdp_sender import SsdpSender as exposed_SsdpSender

    from rpyc.utils.server import ThreadedServer
    t = ThreadedServer(SsdpSenderService, port = 18861, protocol_config = {"allow_public_attrs" : True})
    t.start()

if __name__ == '__main__':
    server()

