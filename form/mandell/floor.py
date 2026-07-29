"""Floor — immutable. More foundational than Dell Matrix."""

FLOOR = ("Alpha", "Delta", "Omega", "Omni")
NOVA_MODE = "Cheat only"  # Nova is not Floor; cheat-only edge


def assert_floor_intact(candidates=None) -> bool:
    if list(FLOOR) != ["Alpha", "Delta", "Omega", "Omni"]:
        raise RuntimeError("Floor integrity failure")
    return True


def floor_status():
    return {"floor": list(FLOOR), "nova": NOVA_MODE, "locked": True}
