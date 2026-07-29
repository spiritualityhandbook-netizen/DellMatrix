# Link Gemini · Grok · Claude · Copilot · AI Studio on Windows

These are **cloud AIs** (API or CLI), not local model downloads.  
Dell Matrix core stays offline; bridges turn on only when keys/CLI exist.

## 1. Install terminal tools (PowerShell as Admin optional)

```powershell
# Git + GitHub CLI (Copilot path)
winget install Git.Git
winget install GitHub.cli

# Python already required for Dell Matrix
gh auth login
gh extension install github/gh-copilot
```

**Google AI Studio / Gemini:** browser → https://aistudio.google.com → API key  
**Claude:** https://console.anthropic.com → API key  
**Grok (xAI):** https://console.x.ai → API key  
**Copilot:** GitHub account with Copilot + `gh auth login`

There is no official “download Claude into cmd” offline app. Keys + CLI is the terminal path.

## 2. Set keys for her user (PowerShell — this session)

```powershell
$env:GOOGLE_API_KEY = "her-gemini-or-aistudio-key"
$env:GEMINI_API_KEY = $env:GOOGLE_API_KEY
$env:XAI_API_KEY = "her-xai-key"
$env:ANTHROPIC_API_KEY = "her-claude-key"
$env:GITHUB_TOKEN = "her-gh-token"   # optional if gh auth already done
```

**Permanent (User env):**  
Windows Settings → System → About → Advanced system settings → Environment Variables → User → New

Never put keys in the DellMatrix git repo.

## 3. Detect what is linked

```powershell
cd $env:USERPROFILE\Documents\DellMatrix
python -m form.llm.cli --detect
```

## 4. Enhance her matrix / trading session

```powershell
python -m form.llm.cli --matrix --owner Sister --provider grok
python -m form.llm.cli --matrix --owner Sister --provider claude
python -m form.llm.cli --matrix --owner Sister --provider gemini
python -m form.llm.cli --matrix --owner Sister --all "Rank risks and next paper trades; not advice"
```

## 5. Daily chain (market evolve + AI enhance)

```powershell
python -m form.trading.cli --owner Sister daily
python -m form.llm.cli --matrix --owner Sister --all "Daily brief from matrix status"
```

## 6. What “universal enhance” means here

| AI | How it links |
|----|----------------|
| Gemini / AI Studio | `GOOGLE_API_KEY` → Gemini API |
| Grok | `XAI_API_KEY` → xAI API |
| Claude | `ANTHROPIC_API_KEY` → Anthropic API |
| Copilot | `gh` CLI authenticated / token |
| Dell Matrix | Always local plane + trading paper |

AIs **suggest**; the matrix **stores and evolves** structure. She decides paper/live orders.

**Not financial advice.**
