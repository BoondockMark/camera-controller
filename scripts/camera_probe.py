from __future__ import annotations

import argparse
from typing import Iterable

import httpx


DEFAULT_CANDIDATES = [
    "/",
    "/ccapi/ver100/",
    "/ccapi/ver100",
    "/api/",
    "/api/ver100/",
    "/api/ver100",
    "/index.html",
    "/index.htm",
]


def build_url_list(ip: str, port: int | None = None) -> list[str]:
    urls: list[str] = []
    base_candidates = [f"http://{ip}", f"http://{ip}:{port or 80}"] if port else [f"http://{ip}"]
    for base in base_candidates:
        for path in DEFAULT_CANDIDATES:
            urls.append(base.rstrip("/") + path)
    return list(dict.fromkeys(urls))


def probe_url(url: str, timeout: float) -> dict[str, object]:
    result: dict[str, object] = {
        "url": url,
        "status": None,
        "server": None,
        "content_type": None,
        "body_excerpt": "",
        "error": None,
    }

    try:
        with httpx.Client(follow_redirects=True, timeout=timeout) as client:
            for method in ("GET", "HEAD", "OPTIONS"):
                try:
                    response = client.request(method, url)
                    result["status"] = response.status_code
                    result["server"] = response.headers.get("server")
                    result["content_type"] = response.headers.get("content-type")
                    result["body_excerpt"] = response.text[:300].replace("\n", " ")
                    print(f"[{method}] {url}")
                    print(f"  status={response.status_code}")
                    print(f"  server={response.headers.get('server')}")
                    print(f"  content-type={response.headers.get('content-type')}")
                    print(f"  body={response.text[:300].replace(chr(10), ' ')}")
                    print()
                    return result
                except Exception as exc:  # keep probing other methods if one fails
                    result["error"] = f"{method}: {type(exc).__name__}: {exc}"
                    print(f"[{method}] {url}")
                    print(f"  ERROR: {type(exc).__name__}: {exc}")
                    print()
    except Exception as exc:
        result["error"] = f"client: {type(exc).__name__}: {exc}"

    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Probe likely Canon camera control endpoints over HTTP.")
    parser.add_argument("--ip", required=True, help="Camera IP address to probe (for example 192.168.1.15)")
    parser.add_argument("--port", type=int, default=80, help="HTTP port to probe")
    parser.add_argument("--timeout", type=float, default=5.0, help="HTTP timeout in seconds")
    args = parser.parse_args()

    print(f"Probing Canon camera at {args.ip}:{args.port}")
    print("This checks common Canon API URLs and their HTTP responses.")
    print()

    for url in build_url_list(args.ip, args.port):
        probe_url(url, timeout=args.timeout)

    print("Done. If one of the URLs returned a non-5xx / non-timeout response, that is a likely API base path.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
