# Give Pack — Hand someone a Blank Dell Matrix

## Fast path (recommended)

```bash
cd preform/seed
python pack_seed.py
```

That:
1. Runs integrity check
2. Builds `BlankDellMatrix-YYYY-MM-DD.zip` next to `seed/`
3. Prints `READY TO SEND`

Send the zip.

Manual check only:
```bash
python check_seed.py
```

---

## What to send
**Blank:** the zip from `pack_seed.py` (or the `seed/` folder)  
**Full living:** whole repo only if they ask for everything

## What you tell them

1. Unzip
2. `cd seed` (folder name may be `seed` inside the zip)
3. `python blank_runner.py`
4. Put notes in `personal/` · scripts in `personal_code/`
5. Do not edit Floor or core registry manors
6. Optional later: `SNAP_TEMPLATE/` → see DISTRIBUTION.md to contribute up

## Checklist (if packing by hand)

- [ ] `python check_seed.py` → READY TO GIVE
- [ ] personal slots empty (or intentional examples only)
- [ ] SNAP_TEMPLATE present
- [ ] Floor still Alpha · Delta · Omega · Omni
