# Sister trading matrix — Windows setup

**Not financial advice.** Paper first. Live risks real money.

## Install Dell Matrix

```powershell
cd $env:USERPROFILE\Documents
git clone https://github.com/spiritualityhandbook-netizen/DellMatrix.git
cd DellMatrix
python -m form.give_blank --owner Sister --empty
python -m form.trading.cli --owner Sister daily
```

## Link AIs (Gemini / Grok / Claude / Copilot / AI Studio)

See **`form/llm/WINDOWS_AI_SETUP.md`**

```powershell
python -m form.llm.cli --detect
python -m form.llm.cli --matrix --owner Sister --all "Daily enhancement"
```

## Schedule

```powershell
powershell -ExecutionPolicy Bypass -File form\trading\windows_register_task.ps1 -Owner Sister
```
