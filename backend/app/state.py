"""Ephemeral, in-memory UI state shared across the single uvicorn process.

Right now it just holds which full-screen overlay (if any) the TV should show —
toggled from a phone, pushed to the TV over the websocket. Resets on restart,
which is the desired behavior for a transient "show the rules" mode.
"""
from __future__ import annotations

# allow-list of overlays the TV knows how to render
OVERLAYS = {"secret_hitler"}


class RuntimeState:
    overlay: str | None = None


state = RuntimeState()
