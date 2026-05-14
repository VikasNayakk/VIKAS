# Anthropic Claude — Setup (Hinglish)

> Bhai, ye file batati hai key ko safely use kaise karna hai. Key kabhi bhi code ya git mein commit mat karna.

---

## 1. Full API key chahiye (sirf ek baar milti hai)

Tumne jo JSON share kiya tha usme **sirf hint tha** (`sk-ant-api03-R2D...igAA`), full key nahi.
Full key Anthropic sirf **create karte waqt ek baar** dikhata hai.

- Agar tumne kahin save ki hai (password manager / notes) → wahan se nikaalo.
- Agar nahi mil rahi → purani revoke karo aur nayi banao:
  1. https://console.anthropic.com/settings/keys
  2. Purani key (`apikey_01Rj2N8SVvo6BePZj99NhmiT`) → **Revoke**
  3. **Create Key** → naam: `Vikas-AI-Agent-OS`
  4. Jo `sk-ant-api03-...` (~108 chars) dikhe → turant copy

---

## 2. Key ko `.env` mein paste karo

File: `VIKAS/AI-Agent-OS/.env` (already created, git-ignored)

```
ANTHROPIC_API_KEY=sk-ant-api03-...your-full-key...
```

`PASTE_FULL_KEY_HERE` ki jagah asli key chipka do. Bas.

---

## 3. Dependencies install karo

PowerShell mein:

```powershell
cd "c:\Users\VikasNayak\OneDrive - Aliens Company\VikasNayak\VIKAS\AI-Agent-OS"
pip install anthropic python-dotenv
```

(ya `pip install -r requirements.txt` pura)

---

## 4. Test karo

```powershell
python scripts\test_anthropic.py
```

Expected output:
```
[OK] Using model: claude-sonnet-4-5
[..] Sending test prompt...
[Claude] Aliens AI online.
```

---

## 5. Kahin bhi use karo

```python
from integrations.anthropic_client import ClaudeClient

claude = ClaudeClient()
reply = claude.ask("Aaj ki Aliens meeting ka summary banao", system="Tum ek meeting assistant ho.")
print(reply)
```

---

## Security checklist

- [x] `.env` git-ignored hai (`.gitignore` mein already hai)
- [x] Code mein key hardcode nahi hai
- [x] Key validation: agar `sk-ant-` se shuru nahi hoti to error
- [ ] **Tum**: full key paste karna hai `.env` mein
- [ ] **Tum**: agar key kabhi chat/screenshot mein leak ho, turant rotate karna
