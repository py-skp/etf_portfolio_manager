import redis
import json
import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# Prioritize Streamlit Secrets for Cloud deployment, fallback to environment/local
REDIS_URL = os.getenv("REDIS_URL")
if not REDIS_URL:
    try:
        REDIS_URL = st.secrets.get("REDIS_URL")
    except:
        pass

if not REDIS_URL:
    REDIS_URL = "redis://redis:6379/0"

class CacheService:
    def __init__(self):
        try:
            self.client = redis.from_url(REDIS_URL)
        except Exception:
            self.client = None
            print("Redis not available, caching disabled.")

    def get(self, key):
        if not self.client:
            return None
        try:
            data = self.client.get(key)
            return json.loads(data) if data else None
        except Exception:
            return None

    def set(self, key, value, ttl=3600):
        if not self.client:
            return False
        try:
            return self.client.setex(key, ttl, json.dumps(value))
        except Exception:
            return False

    def delete(self, key):
        if not self.client:
            return False
        try:
            return self.client.delete(key)
        except Exception:
            return False

    def clear_all(self):
        """Flushes the entire cache database."""
        if not self.client:
            return False
        try:
            return self.client.flushdb()
        except Exception:
            return False

# Singleton instance
cache_service = CacheService()
