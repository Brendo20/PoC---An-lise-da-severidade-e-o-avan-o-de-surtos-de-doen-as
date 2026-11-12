"""Obtém somente o CSV de 2019 previamente auditado e verifica seu SHA-256."""
from __future__ import annotations

import argparse
import hashlib
import os
import tempfile
import urllib.request
from pathlib import Path

URL = "https://s3.sa-east-1.amazonaws.com/ckan.saude.gov.br/SRAG/2019/INFLUD19-23-03-2026.csv"
SHA256 = "f6de547c1234e2de4d65f830606849a006346e50b32106bd635714665100134a"
FILENAME = "INFLUD19-23-03-2026.csv"


def verified_download(destination: Path, *, url: str = URL, expected_hash: str = SHA256,
                      opener=urllib.request.urlopen) -> str:
    if destination.exists():
        with destination.open("rb") as stream:
            actual = hashlib.file_digest(stream, "sha256").hexdigest()
        if actual != expected_hash:
            raise ValueError("Destino existente tem hash diferente; arquivo preservado")
        return "already_verified"
    destination.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix="srag-download-", dir=destination.parent)
    temporary = Path(temporary_name)
    try:
        digest = hashlib.sha256()
        with os.fdopen(descriptor, "wb") as output:
            with opener(url, timeout=60) as response:
                size = 0
                while chunk := response.read(1024 * 1024):
                    size += len(chunk)
                    if size > 512 * 1024 * 1024:
                        raise ValueError("Download excedeu o limite esperado de tamanho")
                    digest.update(chunk)
                    output.write(chunk)
        if digest.hexdigest() != expected_hash:
            raise ValueError("Hash divergente: conteúdo remoto não corresponde ao CSV auditado")
        # Publica o arquivo verificado sem sobrescrever destino criado concorrentemente.
        os.link(temporary, destination)
        return "downloaded_and_verified"
    finally:
        temporary.unlink(missing_ok=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()
    status = verified_download(args.destination)
    print(f"CSV 2019: {status}; SHA-256: {SHA256}")


if __name__ == "__main__":
    main()
