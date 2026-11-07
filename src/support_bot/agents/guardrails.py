import re

from ..prompts import SYSTEM_PROMPT

REFUSAL = (
    "Dabei kann ich leider nicht helfen. Kann ich Ihnen sonst bei einer "
    "Bestellung, Retoure oder allgemeinen Frage weiterhelfen?"
)
PRIVACY_REFUSAL = "Aus Datenschutzgründen kann ich diese Information nicht ausgeben."
MAX_INPUT_CHARS = 1000

EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
IBAN_RE = re.compile(r"\b[A-Z]{2}\d{2}(?:\s?[A-Z0-9]{4}){3,7}\s?[A-Z0-9]{1,4}\b")


INJECTION_PATTERNS = [
    # Anweisungen ignorieren / überschreiben
    r"(ignor|disregard|overrid|bypass|skip|ueberspring|überspring|missacht|umgeh)\w*\W+(\w+\W+){0,4}?"
    r"(instruction|anweisung|regel|rule|prompt|guideline|richtlinie|restriction|vorgabe|filter)",
    r"(vergiss|vergessen|forget)\W+(\w+\W+){0,4}?(anweisung|instruction|regel|rule|alles|everything|prompt)",
    # System-Prompt / interne Regeln erfragen
    r"(show|reveal|print|repeat|display|leak|output|zeig|verrat|gib|nenn|wiederhol|schreib)\w*\W+(\w+\W+){0,6}?"
    r"(system[\s_-]?prompt|anweisungen|instructions|initial prompt|your prompt|deine regeln|your rules)",
    r"(what|was)\W+(\w+\W+){0,3}?(your|deine)\W+(instruction|anweisung|prompt|regel|rule)",
    # Rolle / Persona überschreiben
    r"you are now|du bist (jetzt|ab sofort|nun)|ab sofort bist du|from now on|new instructions|neue anweisungen",
    r"(act|behave|respond)\s+as\b|pretend\s+(to be|you)|tu so als|stell dir vor,? du",
    r"developer mode|entwicklermodus|jailbreak|\bDAN\b|do anything now|god mode",
    # Fake-Systemnachrichten und Chat-Template-Tokens
    r"(^|\n)\s*(system|assistant|developer)\s*:",
    r"\[/?(inst|sys)\]|<\|?(im_start|im_end|system|endoftext)\|?>|###\s*(system|instruction)",
]

INJECTION_RE = re.compile("|".join(INJECTION_PATTERNS), re.IGNORECASE)


_PROMPT_SNIPPETS = [
    line.strip().lower()
    for line in SYSTEM_PROMPT.splitlines()
    if len(line.strip()) > 25
]

def check_input(text: str) -> bool:
    """True = Nachricht darf weiter, False = hoeflich ablehnen."""
    if not text.strip() or len(text) > MAX_INPUT_CHARS:
        return False
    return INJECTION_RE.search(text) is None


def check_output(text: str) -> str | None:
    """None = Antwort ist in Ordnung, sonst die höfliche Ersatzantwort."""
    if EMAIL_RE.search(text) or IBAN_RE.search(text):
        return PRIVACY_REFUSAL
    lowered = text.lower()
    if any(snippet in lowered for snippet in _PROMPT_SNIPPETS):
        return REFUSAL
    return None