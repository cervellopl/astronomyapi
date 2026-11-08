#!/usr/bin/env python3
"""Generate the self-signed certificate the HTTPS listener uses.

Browsers refuse the microphone - and the whole Web Speech API - on an
insecure origin. Anything other than localhost over plain HTTP counts as
insecure, so reaching the app at http://192.168.x.x:5000 means Edge and Chrome
deny the microphone outright, without even offering the permission prompt.

A self-signed certificate is enough: once the warning is accepted the browser
treats the origin as secure, and the microphone works normally. The names and
addresses the certificate covers come from CERT_HOSTS, so it matches whatever
address the app is actually reached at.

Idempotent: an existing certificate with at least a month left is kept.
"""

import datetime
import ipaddress
import os
import socket
import sys

CERT_DIR = os.environ.get('CERT_DIR', '/app/certs')
CERT_FILE = os.path.join(CERT_DIR, 'server.crt')
KEY_FILE = os.path.join(CERT_DIR, 'server.key')


def wanted_hosts():
    """Every name and address the certificate should be valid for."""
    hosts = ['localhost', '127.0.0.1', '::1']
    for extra in (os.environ.get('CERT_HOSTS') or '').split(','):
        extra = extra.strip()
        if extra:
            hosts.append(extra)
    try:
        hosts.append(socket.gethostname())
    except Exception:
        pass
    seen, out = set(), []
    for host in hosts:
        if host not in seen:
            seen.add(host)
            out.append(host)
    return out


def still_valid():
    if not (os.path.isfile(CERT_FILE) and os.path.isfile(KEY_FILE)):
        return False
    try:
        from cryptography import x509
        with open(CERT_FILE, 'rb') as f:
            cert = x509.load_pem_x509_certificate(f.read())
        left = cert.not_valid_after - datetime.datetime.utcnow()
        return left > datetime.timedelta(days=30)
    except Exception:
        return False


def main():
    if still_valid():
        print('certificate already present and valid')
        return 0

    try:
        from cryptography import x509
        from cryptography.x509.oid import NameOID
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import rsa
    except ImportError as e:
        print('cannot build a certificate (%s); HTTPS will stay off' % e)
        return 0                      # never block startup over this

    os.makedirs(CERT_DIR, exist_ok=True)
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    names = []
    for host in wanted_hosts():
        try:
            names.append(x509.IPAddress(ipaddress.ip_address(host)))
        except ValueError:
            names.append(x509.DNSName(host))

    subject = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, u'astronomy observations'),
    ])
    now = datetime.datetime.utcnow()
    certificate = (
        x509.CertificateBuilder()
        .subject_name(subject)
        .issuer_name(subject)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now - datetime.timedelta(days=1))
        .not_valid_after(now + datetime.timedelta(days=3650))
        .add_extension(x509.SubjectAlternativeName(names), critical=False)
        .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
        .sign(key, hashes.SHA256())
    )

    with open(KEY_FILE, 'wb') as f:
        f.write(key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()))
    os.chmod(KEY_FILE, 0o600)
    with open(CERT_FILE, 'wb') as f:
        f.write(certificate.public_bytes(serialization.Encoding.PEM))

    print('certificate written for: %s' % ', '.join(wanted_hosts()))
    return 0


if __name__ == '__main__':
    sys.exit(main())
