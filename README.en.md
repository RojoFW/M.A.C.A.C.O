# M.A.C.A.C.O

[Español](README.md)

A testing tool that sends multiple `POST` requests with synthetic data to a registration endpoint on a local server. It automates the repetitive work of preparing and submitting JSON payloads during authorized volume and repeated request testing. This can help check data validation, responses, and rate limiting controls.

## How it works

`exploit.py` reads `template.json` and creates a fresh payload for each request. Values in the form `|? -> provider|` are replaced with data from [Faker](https://faker.readthedocs.io/); other values are sent as written. Replacement also works inside nested objects and arrays. For example:

```json
{
  "username": "|? -> user_name|",
  "email": "|? -> email|",
  "password": "123456"
}
```

Here, `username` and `email` change with each request, while `password` stays fixed. A placeholder name must match a Faker provider; `|? -> number|` uses the `random_number` provider. The template must be a valid JSON object.

Requests are sent as JSON with a five second timeout, without following redirects. The progress bar shows the latest HTTP status code or connection error type. The final summary counts only HTTP `200` and `201` responses as successful.

## Installation and usage

Requires Python 3 and a local test server with the target endpoint available.

```bash
python3 -m venv venv
source venv/bin/activate
python3 -m pip install -r requirements.txt
python3 exploit.py --host http://127.0.0.1:8000 --endpoint /api/auth/register --count 10 --workers 2
```

Before running the script, edit `template.json` to match the fields accepted by your API. Available options:

| Option | Description | Default |
| --- | --- | --- |
| `--host` | HTTP or HTTPS origin of the local server, without a path. Only `localhost`, `127.0.0.1`, and `::1` are accepted. | `http://127.0.0.1:8000` |
| `--endpoint` | Endpoint path; must start with `/`. | `/api/auth/register` |
| `--count` | Maximum number of requests; must be positive. | `10` |
| `--workers` | Concurrent requests, from `1` to `5`. | `2` |

Faker uses `es_ES` by default. To change the locale, copy `.env.example` to `.env` and set `FAKER_LOCALE`, or set that environment variable directly. The environment variable takes precedence over `.env`.

## Responsible use

This tool is intended for ethical cybersecurity testing on systems you own or have explicit permission to test. Repeated requests may create records and consume resources. Use a test environment, synthetic data, and a request volume agreed with the system owner. Users are responsible for staying within their authorization and complying with applicable laws.

## License

Distributed under the [MIT License](LICENSE). See the license file for its terms and warranty disclaimer.
