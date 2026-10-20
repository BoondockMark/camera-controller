from __future__ import annotations

import argparse
import socket

import httpx

CANON_HOST_PATHS = [
    "/",
    "/ccapi/ver100/",
    "/ccapi/ver100",
    "/ccapi",
    "/api/",
    "/api/ver100/",
    "/api/ver100",
    "/index.html",
    "/index.htm",
    "/MISC/",
    "/camera/",
    "/camera/control",
    "/camera/recording",
    "/download",
    "/live",
    "/status",
    "/ver100/",
    "/ver100",
]


def probe_host(ip: str, port: int, timeout: float) -> None:
    print(f"\n=== Probing {ip}:{port} ===")
    with httpx.Client(follow_redirects=True, timeout=timeout) as client:
        for path in CANON_HOST_PATHS:
            url = f"http://{ip}:{port}{path}"
            print(f"\n--- {url} ---")
            for method in ("GET", "HEAD", "OPTIONS"):
                try:
                    response = client.request(method, url)
                    text = response.text[:500].replace("\n", " ") if response.text else ""
                    print(f"{method}: status={response.status_code} content-type={response.headers.get('content-type')} server={response.headers.get('server')} body={text}")
                except Exception as exc:
                    print(f"{method}: ERROR: {type(exc).__name__}: {exc}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Probe canonical camera control endpoints on the known Canon port.")
    parser.add_argument("--ip", default="192.168.1.15", help="IP address of the camera")
    parser.add_argument("--port", type=int, default=49152, help="Port to probe")
    parser.add_argument("--timeout", type=float, default=5.0, help="HTTP timeout in seconds")
    args = parser.parse_args()

    try:
        with socket.create_connection((args.ip, args.port), timeout=args.timeout):
            print(f"TCP connect successful to {args.ip}:{args.port}")
    except Exception as exc:
        print(f"TCP connect failed to {args.ip}:{args.port}: {type(exc).__name__}: {exc}")
        return

    probe_host(args.ip, args.port, args.timeout)


if __name__ == "__main__":
    main()
