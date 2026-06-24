import re

def clean_for_speech(text: str) -> str:
    """
    Strip markdown/formatting symbols before sending text to TTS.
    Fixes issue #8: AI was reading "-", "*", "#" etc out loud.
    """
    if not text:
        return text

    cleaned = text

    # Remove markdown bold/italic markers: **text** -> text, *text* -> text
    cleaned = re.sub(r"\*\*(.+?)\*\*", r"\1", cleaned)
    cleaned = re.sub(r"\*(.+?)\*", r"\1", cleaned)

    # Remove markdown headers: "### Title" -> "Title"
    cleaned = re.sub(r"^#{1,6}\s*", "", cleaned, flags=re.MULTILINE)

    # Convert bullet markers at line start ("- ", "* ", "• ") into a pause (period)
    cleaned = re.sub(r"^[\-\*\u2022]\s+", "", cleaned, flags=re.MULTILINE)

    # Remove numbered-list markers like "1. " "2) " at line start
    cleaned = re.sub(r"^\d+[\.\)]\s+", "", cleaned, flags=re.MULTILINE)

    # Remove markdown links/inline code/backticks
    cleaned = re.sub(r"`([^`]*)`", r"\1", cleaned)
    cleaned = re.sub(r"\[(.*?)\]\((.*?)\)", r"\1", cleaned)

    # Remove stray symbols that have no spoken meaning
    cleaned = re.sub(r"[#_~|>]+", " ", cleaned)

    # Collapse multiple spaces/newlines
    cleaned = re.sub(r"[ \t]+", " ", cleaned)
    cleaned = re.sub(r"\n{2,}", ". ", cleaned)
    cleaned = re.sub(r"\n", ". ", cleaned)
    cleaned = re.sub(r"\.\s*\.", ".", cleaned)

    return cleaned.strip()
