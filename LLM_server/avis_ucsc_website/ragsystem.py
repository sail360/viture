"""
Medha system context, roles, and permissions provider for LLM usage, wrapping LibrarianClient.
"""

import os
from typing import Any, Dict, Optional
import logging

from dotenv import load_dotenv

from .librarian_client import LibrarianClient

load_dotenv()
logger = logging.getLogger(__name__)


MEDHA_URL="http://0.0.0.0:8051"
MEDHA_LOCAL_TOKEN="gs19qyzc0aZpTY1HYDF7Nz5lArEahLleIIgq8LTb"
MEDHA_CLOUD_TOKEN="gs19qyzc0aZpTY1HYDF7Nz5lArEahLleIIgq8LTb"
MEDHA_TIMEOUT_SECONDS="10.0"
MEDHA_ACCESS_MODE="cloud"

class RAGSystem:
    def __init__(self, collections: Optional[list[str]] = None):
        medha_url = MEDHA_URL
        if MEDHA_ACCESS_MODE == "local":
            print("Using local type MEDHA")
            medha_token = MEDHA_LOCAL_TOKEN
        else:
            print("Using cloud type MEDHA")
            medha_token = MEDHA_CLOUD_TOKEN

        self.medha_client = LibrarianClient(
            base_url=medha_url,
            token=medha_token,
            timeout=float(os.getenv("MEDHA_TIMEOUT_SECONDS") or "10.0"),
        )
        print(f"Using MEDHA at {medha_url}")
        self.collections = collections or ["shared"]

    def get_context(self, prompt: str) -> str:
        try:
            payload = self.medha_client.query(
                query=prompt,
                limit=int(os.getenv("LIBRARIAN_TOP_K") or "4"),
            )

            results = payload.get("results", {})
            if not results:
                return ""

            documents = results.get("documents", [[]])[0]
            metadatas = results.get("metadatas", [[]])[0]
            distances = results.get("distances", [[]])[0]

            blocks = []
            for idx, (content, meta, distance) in enumerate(
                zip(documents, metadatas, distances), start=1
            ):
                meta = meta or {}
                title = meta.get("filename", meta.get("document_id", "Untitled"))
                collection = meta.get("relative_path", "unknown")
                content = (content or "").strip()

                if content:
                    blocks.append(
                        f"[{idx}] {title} ({collection})\nscore={distance}\n{content}"
                    )

            return "\n\n".join(blocks)

        except Exception as e:
            logger.info("Interrupt handler failed: %s", e)
            return ""
