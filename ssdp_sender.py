#!/usr/bin/env python

import socket
import sys
import struct
import select

def make_ipv4_header(srcip, dstip, datal):
    srcip = socket.inet_aton(srcip)
    dstip = socket.inet_aton(dstip)

    ver        = 4               #Version 4 for IPv4
    ihl        = 5               #Header length in 32 bit words. 5 words == 20 bytes
    dscp_ecn   = 0               #Optional fields, don't feel like implementing. Let's keep it at 0
    tlen       = datal + 20      #Length of data + 20 bytes for ipv4 header
    ident      = socket.htons(0) #ID of packet
    flg_frgoff = 0               #Flags and fragment offset
    ttl        = 1               #Time to live
    ptcl       = 17              #Protocol, 17 (UDP)
    chksm      = 0               #Will automatically fill in checksum    

    tlen       = socket.htons(tlen)
    flg_frgoff = socket.htons(flg_frgoff)

    return struct.pack(
        "!"     #Network(Big endian)
        "2B"    #Version and IHL, DSCP and ECN
        "3H"    #Total Length, Identification, Flags and Fragment Offset
        "2B"    #Time to live, Protocol
        "H"     #Checksum
        "4s"    #Source ip
        "4s"    #Destination ip
        , (ver << 4) + ihl, dscp_ecn, tlen, ident, flg_frgoff, ttl, ptcl, chksm, srcip, dstip)

def make_udp_header(srcprt, dstprt, datal):
    return struct.pack(
        "!4H"   #Source port, Destination port, Length, Checksum
        , srcprt, dstprt, datal+8, 0)

class SsdpSender():
    def __init__(self):
        
        self.socket_v4 = socket.socket(socket.AF_INET,
                                       socket.SOCK_RAW,
                                       socket.IPPROTO_IP)
        self.socket_v4.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

        #self.socket_v6 = socket.socket(socket.AF_INET6,
        #                               socket.SOCK_RAW,
        #                               socket.IPPROTO_IP)
        #self.socket_v6.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

    def send(self, data, family, src, dst):
        uh = make_udp_header (src[1], dst[1], len(data))
        ph = make_ipv4_header(src[0], dst[0], len(data)+len(uh))
        packet = ph+uh+data
        print ':'.join('{:02x}'.format(ord(c)) for c in packet)
        if   family == socket.AF_INET:
            self.socket_v4.sendto(packet, dst)
        #elif family == socket.AF_INET6:
        #    self.socket_v6.sendto(packet, dst)
        else:
            raise "Socket family not implemented"


def main():
    sender = SsdpSender()
    sender.send('', socket.AF_INET, ('192.168.4.1', 9999), ('239.255.255.250', 1900))
    return

if __name__ == '__main__':
    main()


