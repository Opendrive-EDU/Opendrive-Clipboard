"""Optional Speechify text-to-speech provider (instructor-approved audio only).

Disabled by default. This mirrors the ``GeminiDraftProvider`` optional-provider
guard in ``agent.py``: the demo, judge dry-runs, and the Docker build's offline
unittest never depend on network access or the Speechify SDK being installed.

Brand / licensing posture
-------------------------
The judge-facing default is a professional voice. "Youth Mode" (an energetic /
celebrity voice such as Snoop Dogg) is opt-in, instructor-gated, and only ever
speaks text a licensed instructor has already approved. A celebrity voice is
used ONLY if the configured voice id is available on the account's plan and
licensed for redistribution; any SDK / voice / network error falls back to the
professional voice and is flagged (``voice_fell_back=True``). Speechify never
authors or alters the debrief — it only reads back already-approved text.
"""

from __future__ import annotations

import base64
import os

# Speechify hard-caps request size; stay well under it and bound PAYG cost.
MAX_TTS_CHARS = 3000


def tts_enabled() -> bool:
    """True only when TTS is explicitly switched on and a key is present."""
    return os.getenv("SPEECHIFY_ENABLE_TTS") == "true" and bool(
        os.getenv("SPEECHIFY_API_KEY")
    )


def _voice_for(mode: str) -> tuple[str, str]:
    """Return ``(requested_voice_id, professional_fallback_voice_id)``."""
    professional = os.getenv("SPEECHIFY_VOICE_DEFAULT", "scott")
    if mode == "youth":
        return os.getenv("SPEECHIFY_VOICE_YOUTH", professional), professional
    return professional, professional


def synthesize(text: str, mode: str = "professional") -> dict:
    """Synthesize already-instructor-approved text to base64 audio.

    Returns ``{"enabled": False}`` when TTS is not configured (the default
    state) so callers degrade gracefully and offline tests never hit the
    network. The caller is responsible for enforcing instructor approval
    before calling this function.
    """
    if not tts_enabled():
        return {"enabled": False}

    clean = (text or "").strip()
    if not clean:
        raise ValueError("Nothing to synthesize: empty text.")

    truncated = len(clean) > MAX_TTS_CHARS
    clipped = clean[:MAX_TTS_CHARS]

    requested_voice, fallback_voice = _voice_for(mode)

    # Lazy import: the SDK is only needed when TTS is actually enabled, so the
    # offline Docker build / unittest never requires the package.
    from speechify import Speechify

    client = Speechify(token=os.environ["SPEECHIFY_API_KEY"])

    voice_used = requested_voice
    voice_fell_back = False
    try:
        audio_b64 = _speak(client, clipped, requested_voice)
    except Exception:  # noqa: BLE001 - unknown/unlicensed voice or network error
        if requested_voice == fallback_voice:
            raise ValueError("Speechify synthesis failed.")
        voice_used = fallback_voice
        voice_fell_back = True
        try:
            audio_b64 = _speak(client, clipped, fallback_voice)
        except Exception as exc:  # noqa: BLE001
            raise ValueError("Speechify synthesis failed.") from exc

    return {
        "enabled": True,
        "audio_b64": audio_b64,
        "mime": "audio/mpeg",
        "voice": voice_used,
        "mode": "youth" if mode == "youth" else "professional",
        "voice_fell_back": voice_fell_back,
        "chars": len(clipped),
        "truncated": truncated,
    }


def _speak(client, text: str, voice_id: str) -> str:
    """Call Speechify and return base64-encoded MP3 audio.

    The SDK has returned ``audio_data`` as either a base64 ``str`` or raw
    ``bytes`` across versions; handle both so a minor SDK bump can't break the
    live demo.
    """
    result = client.tts.audio.speech(input=text, voice_id=voice_id)

    audio = getattr(result, "audio_data", None)
    if audio is None and isinstance(result, dict):
        audio = result.get("audio_data")
    if audio is None:
        raise ValueError("Speechify returned no audio_data.")

    if isinstance(audio, (bytes, bytearray)):
        return base64.b64encode(bytes(audio)).decode("ascii")
    return audio
