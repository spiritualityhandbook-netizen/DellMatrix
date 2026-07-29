# Sister trading matrix — Windows setup

**Not financial advice.** Paper trading is simulated. Live trading can lose real money.

## 1. Install

1. Install [Python 3](https://www.python.org/downloads/) — check **Add Python to PATH**.
2. Open **PowerShell**.
3. Clone:

```powershell
cd $env:USERPROFILE\Documents
git clone https://github.com/spiritualityhandbook-netizen/DellMatrix.git
cd DellMatrix
```

(No git? Download ZIP from GitHub → Extract → `cd` into folder.)

## 2. Create her blank + trading session

```powershell
python -m form.give_blank --owner Sister --empty
python -m form.trading.cli --owner Sister daily
python -m form.trading.cli --owner Sister status
```

## 3. Daily commands (terminal)

```powershell
cd $env:USERPROFILE\Documents\DellMatrix

python -m form.trading.cli --owner Sister daily      # market sim + ideas + evolve + save
python -m form.trading.cli --owner Sister status
python -m form.trading.cli --owner Sister buy SPY 1  # paper only
python -m form.trading.cli --owner Sister sell SPY 1
python -m form.trading.cli --owner Sister evolve 10

python -m form.repl --owner Sister --load             # full matrix REPL
```

Inside REPL she can still `place`, `grow ideas`, `visual`, `save`.

## 4. Schedule daily update (Task Scheduler)

```powershell
cd $env:USERPROFILE\Documents\DellMatrix
powershell -ExecutionPolicy Bypass -File form\trading\windows_register_task.ps1 -Owner Sister
```

Or manual: Task Scheduler → Create Task → Daily → Action:
`python`  Arguments: `-m form.trading.cli --owner Sister daily`  Start in: `...\DellMatrix`

## 5. Start matrix REPL on logon (optional)

Use `windows_register_task.ps1 -Owner Sister -LogonRepl`

## 6. Live trading (optional — her keys only)

```powershell
$env:TRADING_LIVE = "1"
$env:TRADING_API_KEY = "her_key"
$env:TRADING_API_SECRET = "her_secret"
$env:TRADING_BASE_URL = "https://broker-api.example"
```

Live orders stay **stubbed** until she (or you) wires her broker SDK inside `form/trading/broker.py` → `LiveBrokerStub.order`.  
**Do not commit keys to GitHub.**

## 7. What evolves daily

- Simulated (or later live-fed) quotes → top movers become **plane ideas**
- **IdeaGrow** + **DuoBeta** generation tick
- Paper broker state saved under `form/state/trading/`
- Matrix program save under `form/state/program_Sister.json`

Mandell Floor stays locked. Her cube stays hers.
