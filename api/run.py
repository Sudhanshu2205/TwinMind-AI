"""Vercel serverless function for POST /api/run.

Imports the business logic from app.py so there is zero duplication.
"""

from __future__ import annotations

import json
import os
import sys
from http.server import BaseHTTPRequestHandler

# Allow importing from the project root (one level above api/).
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app import GenerationRequest, EducationalContentPipeline  # noqa: E402

PIPELINE = EducationalContentPipeline()


class handler(BaseHTTPRequestHandler):
    """Vercel Python runtime expects a class named ``handler``."""

    def do_POST(self) -> None:
        content_length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(content_length)

        try:
            payload = json.loads(raw_body.decode("utf-8"))
            request = GenerationRequest.from_payload(payload)
            result = PIPELINE.run(request)
            self._respond(200, result)
        except ValueError as error:
            self._respond(400, {"error": str(error)})
        except json.JSONDecodeError:
            self._respond(400, {"error": "Body must be valid JSON."})
        except Exception as error:
            self._respond(500, {"error": f"Unexpected server error: {error}"})

    def _respond(self, status: int, payload: dict) -> None:
        body = json.dumps(payload, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
