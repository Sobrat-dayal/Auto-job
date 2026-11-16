"""Standalone executable entry point for AUTONOM backend sidecar."""

import argparse
import os
import sys

import uvicorn


def main() -> None:
    parser = argparse.ArgumentParser(description="AUTONOM Backend Sidecar Service")
    parser.add_argument("--host", default="127.0.0.1", help="Loopback host to bind (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8765, help="Port to bind (default: 8765)")
    parser.add_argument("--api-key", default=None, help="Local API authentication key")
    parser.add_argument("--log-level", default="info", help="Logging level (default: info)")

    args = parser.parse_args()

    # Pass API key into environment if provided via CLI flag
    if args.api_key:
        os.environ["AUTONOM_API_KEY"] = args.api_key

    # Make sure services/api directory or bundle root is on sys.path
    bundle_dir = getattr(sys, "_MEIPASS", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if bundle_dir not in sys.path:
        sys.path.insert(0, bundle_dir)

    print(f"[AUTONOM-SIDECAR] Starting backend service on {args.host}:{args.port}...")
    uvicorn.run(
        "app.main:app",
        host=args.host,
        port=args.port,
        log_level=args.log_level,
        access_log=False,
    )


if __name__ == "__main__":
    main()
