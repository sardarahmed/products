
import json
import os
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

class StorageManager:
    def __init__(self, file_path='history.json'):
        self.file_path = file_path
        self.seen_links = self._load_history()

    def _load_history(self) -> set:
        if not os.path.exists(self.file_path):
            return set()
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return set(data)
        except json.JSONDecodeError:
            logger.error("Failed to decode history.json, starting fresh.")
            return set()
        except Exception as e:
            logger.error(f"Error loading history: {e}")
            return set()

    def save_history(self):
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(list(self.seen_links), f, indent=2)
        except Exception as e:
            logger.error(f"Error saving history: {e}")

    def is_new(self, link: str) -> bool:
        return link not in self.seen_links

    def add(self, link: str):
        self.seen_links.add(link)
