#!/usr/bin/python
import socket
import geoip

def sendPacket(icmp,udp,ttl,dest_name):
    port = 33434
    recv_socket = socket.socket(socket.AF_INET, socket.SOCK_RAW, icmp)            
    send_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, udp)          
    send_socket.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)
    send_socket.settimeout(3.0)
    recv_socket.settimeout(4.0)
    recv_socket.bind(("", port))
    send_socket.sendto("", (dest_name, port))
    curr_addr = None
    curr_name = None
    try:
        _, curr_addr = recv_socket.recvfrom(512)
        curr_addr = curr_addr[0]
        try:
            curr_name = socket.gethostbyaddr(curr_addr)[0]
        except socket.error:
            curr_name = curr_addr
    except socket.error:                                                        
        print "%d\t%s\t%s" % (ttl,'*','*')
        return "unavaible"
    finally:
        send_socket.close()
        recv_socket.close()

    if curr_addr is not None:
        curr_host = "%s (%s)" % (curr_name, curr_addr)
    else:
        curr_host = "*"
    print "{:d}\t{:70s}".format(ttl, curr_host),
    print "%s"%(geoip.geoip(curr_addr))                                        
    return curr_addr


def traceroute(dest_name):
    dest_addr = socket.gethostbyname(dest_name)
    max_hops = 50
    icmp = socket.getprotobyname('icmp')
    udp = socket.getprotobyname('udp')
    ttl = 1
    while True:
        curr_addr = sendPacket(icmp,udp,ttl,dest_name)
        ttl += 1
        if curr_addr == dest_addr or ttl > max_hops:
            break

if __name__ == "__main__":
    traceroute('blog.slinuxer.com')
