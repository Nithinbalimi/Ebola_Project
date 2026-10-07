"""
Custom management command: runhttps
Starts the Django development server over HTTPS using Python 3.13-compatible
ssl.SSLContext API (ssl.wrap_socket was removed in Python 3.12+).
Uses ThreadingMixIn so POST requests and CSRF work correctly.
"""

import ssl
import os
import socketserver
from wsgiref.simple_server import WSGIServer, WSGIRequestHandler

from django.core.management.base import BaseCommand
from django.core.servers.basehttp import get_internal_wsgi_application
from django.conf import settings


class ThreadedWSGIServer(socketserver.ThreadingMixIn, WSGIServer):
    """Threaded WSGI server - handles concurrent requests and Django POST/CSRF correctly."""
    daemon_threads = True
    allow_reuse_address = True


class SSLHandler(WSGIRequestHandler):
    """Request handler that sets https scheme so Django CSRF works on POST."""
    def log_message(self, format, *args):
        print(f"[HTTPS] {self.address_string()} - {format % args}")

    def get_environ(self):
        env = super().get_environ()
        env['wsgi.url_scheme'] = 'https'
        return env


class Command(BaseCommand):
    help = "Start Django dev server over HTTPS (Python 3.13 compatible, threaded)"

    def add_arguments(self, parser):
        parser.add_argument(
            "addrport",
            nargs="?",
            default="127.0.0.1:8443",
            help="ipaddr:port to bind (default: 127.0.0.1:8443)",
        )
        parser.add_argument(
            "--certificate",
            default=getattr(settings, "SSL_CERTIFICATE", None),
            help="Path to SSL certificate (.crt)",
        )
        parser.add_argument(
            "--key",
            default=getattr(settings, "SSL_PRIVATE_KEY", None),
            help="Path to SSL private key (.key)",
        )

    def handle(self, *args, **options):
        addrport = options["addrport"]
        if ":" in addrport:
            addr, port = addrport.rsplit(":", 1)
        else:
            addr = "127.0.0.1"
            port = addrport

        port = int(port)
        cert_file = options["certificate"]
        key_file  = options["key"]

        if not cert_file or not os.path.exists(cert_file):
            self.stderr.write(self.style.ERROR(f"SSL certificate not found: {cert_file}"))
            return
        if not key_file or not os.path.exists(key_file):
            self.stderr.write(self.style.ERROR(f"SSL key not found: {key_file}"))
            return

        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ssl_context.load_cert_chain(certfile=cert_file, keyfile=key_file)

        application = get_internal_wsgi_application()

        httpd = ThreadedWSGIServer((addr, port), SSLHandler)
        httpd.set_app(application)
        httpd.socket = ssl_context.wrap_socket(httpd.socket, server_side=True)

        display_addr = "localhost" if addr == "0.0.0.0" else addr
        self.stdout.write(self.style.SUCCESS(f"\n[HTTPS] Server is running!"))
        self.stdout.write(self.style.SUCCESS(f"   This PC      -> https://{display_addr}:{port}/"))
        if addr == "0.0.0.0":
            import socket as _socket
            try:
                lan_ip = _socket.gethostbyname(_socket.gethostname())
                self.stdout.write(self.style.SUCCESS(f"   Other devices -> https://{lan_ip}:{port}/"))
            except Exception:
                pass
        self.stdout.write("\n   Click Advanced -> Proceed in browser for self-signed cert warning.")
        self.stdout.write("   Press CTRL+C to stop.\n")

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            self.stdout.write("\n[HTTPS] Server stopped.")
