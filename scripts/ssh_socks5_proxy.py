#!/usr/bin/env python3
"""Tiny SOCKS5 stdio relay for OpenSSH ProxyCommand."""

from __future__ import annotations

import os
import socket
import struct
import sys
import threading


def socks5_connect(proxy_host: str, proxy_port: int, target_host: str, target_port: int) -> socket.socket:
    sock = socket.create_connection((proxy_host, proxy_port), timeout=20)
    sock.settimeout(20)
    sock.sendall(b"\x05\x01\x00")
    method = sock.recv(2)
    if method != b"\x05\x00":
        raise RuntimeError(f"SOCKS5 proxy rejected no-auth method: {method!r}")

    host = target_host.encode("idna")
    if len(host) > 255:
        raise RuntimeError("target host is too long for SOCKS5 domain form")
    request = b"\x05\x01\x00\x03" + bytes([len(host)]) + host + struct.pack("!H", target_port)
    sock.sendall(request)
    response = sock.recv(4)
    if len(response) != 4 or response[0] != 5:
        raise RuntimeError(f"invalid SOCKS5 response: {response!r}")
    if response[1] != 0:
        raise RuntimeError(f"SOCKS5 connect failed with code {response[1]}")

    atyp = response[3]
    if atyp == 1:
        to_read = 4
    elif atyp == 3:
        length = sock.recv(1)
        if not length:
            raise RuntimeError("SOCKS5 response missing domain length")
        to_read = length[0]
    elif atyp == 4:
        to_read = 16
    else:
        raise RuntimeError(f"unknown SOCKS5 address type: {atyp}")
    bound_addr = sock.recv(to_read)
    bound_port = sock.recv(2)
    if len(bound_addr) != to_read or len(bound_port) != 2:
        raise RuntimeError("truncated SOCKS5 bind response")
    sock.settimeout(None)
    return sock


def copy_stdin_to_socket(sock: socket.socket) -> None:
    try:
        while True:
            chunk = os.read(sys.stdin.fileno(), 65536)
            if not chunk:
                try:
                    sock.shutdown(socket.SHUT_WR)
                except OSError:
                    pass
                return
            sock.sendall(chunk)
    except OSError:
        return


def copy_socket_to_stdout(sock: socket.socket) -> None:
    try:
        while True:
            chunk = sock.recv(65536)
            if not chunk:
                return
            os.write(sys.stdout.fileno(), chunk)
    except OSError:
        return


def main() -> int:
    if len(sys.argv) != 5:
        print(
            "usage: ssh_socks5_proxy.py <proxy_host> <proxy_port> <target_host> <target_port>",
            file=sys.stderr,
        )
        return 2
    proxy_host = sys.argv[1]
    proxy_port = int(sys.argv[2])
    target_host = sys.argv[3]
    target_port = int(sys.argv[4])
    sock = socks5_connect(proxy_host, proxy_port, target_host, target_port)
    writer = threading.Thread(target=copy_stdin_to_socket, args=(sock,), daemon=True)
    writer.start()
    copy_socket_to_stdout(sock)
    try:
        sock.close()
    except OSError:
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
