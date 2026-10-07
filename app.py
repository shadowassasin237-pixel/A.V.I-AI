"""
A.V.I. - Artificial Voice Intelligence
Main Application Entry Point
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.resolve()

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from config import (
    OPENROUTER_API_KEY,
    LLM_MODEL,
    LIVEKIT_URL,
    LIVEKIT_API_KEY,
    LIVEKIT_API_SECRET,
)
from core.brain import AVIBrain
from voice.agent_launcher import AVIAgentLauncher
from voice.boot_voice import play_boot_voice
from voice.speaker import AVISpeaker
from ui.gui import AVIGUI


def main():
    print("=" * 60)
    print("A.V.I. - Artificial Voice Intelligence")
    print("=" * 60)
    print(f"  Project root : {PROJECT_ROOT}")
    print("  LLM provider : OpenRouter")
    print(f"  LLM model    : {LLM_MODEL}")
    print(
        "  LLM key      : "
        f"{'(set)' if OPENROUTER_API_KEY else '(not set)'}"
    )
    print()
    print("  Voice provider : Inworld via LiveKit")
    print("  Voice          : Arjun (Indian English)")
    print("  TTS model      : inworld/inworld-tts-2")
    print(
        "  LiveKit config : "
        + ("(set)" if all((LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET)) else "(INCOMPLETE)")
    )
    print()

    if not all((LIVEKIT_URL, LIVEKIT_API_KEY, LIVEKIT_API_SECRET)):
        print("A.V.I. ERROR: Priya TTS cannot start because LiveKit credentials are missing.")
        print("Set LIVEKIT_URL, LIVEKIT_API_KEY and LIVEKIT_API_SECRET in .env.")
        print("The application will continue, but voice output will remain disabled.")
        print()

    brain = AVIBrain(
        api_key=OPENROUTER_API_KEY,
        model=LLM_MODEL,
    )

    # Start the LiveKit worker before the desktop room/client.
    agent_launcher = AVIAgentLauncher()
    if not agent_launcher.start():
        print("A.V.I. WARNING: LiveKit agent did not start cleanly. Voice may be unavailable.")

    speaker = AVISpeaker()

    try:
        # Wait for the real Priya agent before any boot speech.
        # This avoids the startup race that previously dropped the intro.
        if speaker.wait_until_ready(timeout=45):
            play_boot_voice(speaker)
        else:
            print("A.V.I. WARNING: Priya was not ready in time; continuing without boot audio.")

        print()
        print("Starting graphical interface...")
        print()

        app = AVIGUI(
            brain=brain,
            speaker=speaker,
        )

        app.mainloop()

    except KeyboardInterrupt:
        print()
        print("A.V.I.: Shutdown requested.")

    finally:
        try:
            speaker.close()
        except Exception:
            pass

        agent_launcher.stop()


if __name__ == "__main__":
    main()
