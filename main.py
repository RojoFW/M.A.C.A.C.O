"""Prueba acotada del registro en un servidor local."""

import argparse
import json
import os
import re
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.parse import urlparse

import requests
from faker import Faker
from faker.config import AVAILABLE_LOCALES
from tqdm import tqdm

TEMPLATE_PATH = Path(__file__).with_name("template.json")
ENV_PATH = Path(__file__).with_name(".env")
PLACEHOLDER = re.compile(r"\|\?\s*->\s*([a-zA-Z][a-zA-Z0-9_]*)\s*\|")


def load_locale():
    locale = "es_ES"
    if ENV_PATH.exists():
        for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            if key.strip() == "FAKER_LOCALE":
                locale = value.strip().strip('"\'')
    locale = os.environ.get("FAKER_LOCALE", locale)
    if locale not in AVAILABLE_LOCALES:
        raise ValueError(f"Idioma de Faker desconocido: {locale}")
    return locale


def placeholders(value):
    if isinstance(value, dict):
        for item in value.values():
            yield from placeholders(item)
    elif isinstance(value, list):
        for item in value:
            yield from placeholders(item)
    elif isinstance(value, str):
        match = PLACEHOLDER.fullmatch(value)
        if match:
            yield match.group(1)
        elif value.startswith("|?"):
            raise ValueError(f"Marcador inválido: {value!r}")


def load_template(locale):
    try:
        template = json.loads(TEMPLATE_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"No se pudo leer {TEMPLATE_PATH}: {exc}") from exc
    if not isinstance(template, dict):
        raise ValueError("La plantilla debe ser un objeto JSON")

    fake = Faker(locale)
    for name in set(placeholders(template)):
        provider = "random_number" if name == "number" else name
        try:
            fake.get_formatter(provider)
        except AttributeError as exc:
            raise ValueError(f"Proveedor de Faker desconocido: {name}") from exc
    return template


def render(value, fake):
    if isinstance(value, dict):
        return {key: render(item, fake) for key, item in value.items()}
    if isinstance(value, list):
        return [render(item, fake) for item in value]
    if isinstance(value, str):
        match = PLACEHOLDER.fullmatch(value)
        if match:
            name = match.group(1)
            generated = fake.format("random_number" if name == "number" else name)
            return json.loads(json.dumps(generated, default=str))
    return value


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="http://127.0.0.1:8000")
    parser.add_argument("--endpoint", default="/api/auth/register")
    parser.add_argument("--count", type=int, default=10, help="Número máximo de solicitudes")
    parser.add_argument("--workers", type=int, default=2, help="Solicitudes simultáneas (máximo 5)")
    args = parser.parse_args()

    host = urlparse(args.host)
    if host.path not in {"", "/"} or host.query or host.fragment:
        parser.error("--host debe contener solo el origen; usa --endpoint para la ruta")
    if not args.endpoint.startswith("/") or args.endpoint.startswith("//"):
        parser.error("--endpoint debe empezar con una sola barra (/)")
    if args.count < 1 or not 1 <= args.workers <= 5:
        parser.error("--count debe ser positivo y --workers debe estar entre 1 y 5")
    return args


def register(url, template, locale, stop_event):
    if stop_event.is_set():
        return None

    fake = Faker(locale)
    data = render(template, fake)
    try:
        response = requests.post(url, json=data, timeout=5, allow_redirects=False)
        return response.status_code
    except requests.RequestException as exc:
        return type(exc).__name__


def main():
    args = parse_args()
    try:
        locale = load_locale()
        template = load_template(locale)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc
    url = args.host.rstrip("/") + args.endpoint
    stop_event = threading.Event()
    successes = 0
    executor = ThreadPoolExecutor(max_workers=args.workers)
    pending = set()

    try:
        with tqdm(total=args.count, desc="Solicitudes", unit="solicitud") as progress:
            for _ in range(min(args.count, args.workers)):
                pending.add(executor.submit(register, url, template, locale, stop_event))

            while pending:
                future = next(as_completed(pending))
                pending.remove(future)
                result = future.result()
                if result is not None:
                    progress.update(1)
                    successes += result in (200, 201)
                    progress.set_postfix_str(f"Estado: {result}")
                if progress.n + len(pending) < args.count:
                    pending.add(executor.submit(register, url, template, locale, stop_event))
    except KeyboardInterrupt:
        stop_event.set()
        print("\nDeteniendo solicitudes...")
    finally:
        stop_event.set()
        executor.shutdown(wait=True, cancel_futures=True)
        print(f"Solicitudes exitosas: {successes}")


if __name__ == "__main__":
    main()
