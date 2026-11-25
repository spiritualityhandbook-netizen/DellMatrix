#!/usr/bin/env python3
"""
Fourier cores for DellMatrix — offline, pure Python.

Freshman picture:
  DFT  = "what pure notes are mixed into this list of samples?"
  FT   = same idea for signals that do not repeat forever

Links: Euler e^{iθ}, rotating vectors, HarmonicLattice, oscillation.
Boolean host · Floor · Nursery intact.
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence, Tuple
import math
import cmath


def _cis(theta: float) -> complex:
    """e^{iθ} = cosθ + i sinθ (Euler)."""
    return complex(math.cos(theta), math.sin(theta))


def dft(samples: Sequence[float]) -> List[complex]:
    """
    Discrete Fourier Transform (naive O(N²), educational).

    Input: list of real samples of one period (or any finite window).
    Output: list of complex coefficients X[k].
      |X[k]|  → strength of frequency k
      angle   → phase of that pure tone
    """
    N = len(samples)
    if N == 0:
        return []
    X: List[complex] = []
    for k in range(N):
        s = 0.0j
        for n, x in enumerate(samples):
            s += x * _cis(-2.0 * math.pi * k * n / N)
        X.append(s)
    return X


def idft(coeffs: Sequence[complex]) -> List[float]:
    """Inverse DFT — rebuild the samples from the coefficients."""
    N = len(coeffs)
    if N == 0:
        return []
    out: List[float] = []
    for n in range(N):
        s = 0.0j
        for k, c in enumerate(coeffs):
            s += c * _cis(2.0 * math.pi * k * n / N)
        out.append((s / N).real)
    return out


def spectrum(samples: Sequence[float]) -> List[Dict[str, Any]]:
    """Human-readable magnitude + phase for each bin."""
    X = dft(samples)
    N = len(X)
    rows = []
    for k, c in enumerate(X):
        mag = abs(c)
        phase = cmath.phase(c) if mag > 1e-12 else 0.0
        # for real signals, bins k and N-k are mirrors; report 0..N//2 as primary
        rows.append({
            "k": k,
            "freq_frac": k / N,          # fraction of sample rate
            "magnitude": round(mag, 6),
            "phase_rad": round(phase, 6),
            "re": round(c.real, 6),
            "im": round(c.imag, 6),
        })
    return rows


def dominant_frequencies(samples: Sequence[float], top: int = 5) -> List[Dict[str, Any]]:
    """Strongest non-DC frequency bins (useful for harmonic locking)."""
    rows = spectrum(samples)
    # skip DC (k=0) for "musical" content; keep it if you want average
    candidates = [r for r in rows if r["k"] != 0]
    # for real signals prefer k <= N/2
    N = len(samples)
    candidates = [r for r in candidates if r["k"] <= N // 2]
    candidates.sort(key=lambda r: r["magnitude"], reverse=True)
    return candidates[: max(1, top)]


def synthesize(coeffs: Sequence[complex], n_samples: Optional[int] = None) -> List[float]:
    """Rebuild waveform from coefficient list (idft wrapper)."""
    if n_samples is not None and n_samples != len(coeffs):
        # pad or trim coefficient list
        c = list(coeffs)[:n_samples]
        while len(c) < n_samples:
            c.append(0.0j)
        return idft(c)
    return idft(coeffs)


def make_sine(n: int = 64, freq: float = 3.0, phase: float = 0.0, amp: float = 1.0) -> List[float]:
    """Test signal: pure sine of frequency `freq` cycles over n samples."""
    return [amp * math.sin(2.0 * math.pi * freq * i / n + phase) for i in range(n)]


def make_square(n: int = 64, freq: float = 1.0) -> List[float]:
    """Test signal: square wave (odd harmonics)."""
    return [1.0 if math.sin(2.0 * math.pi * freq * i / n) >= 0 else -1.0 for i in range(n)]


# ---------------------------------------------------------------------------
# Continuous / non-periodic intuition (educational numerical helpers)
# ---------------------------------------------------------------------------

def continuous_ft_sample(
    signal_fn,
    t_min: float = -5.0,
    t_max: float = 5.0,
    n_t: int = 256,
    f_min: float = -5.0,
    f_max: float = 5.0,
    n_f: int = 128,
) -> Dict[str, Any]:
    """
    Numerical sketch of the continuous Fourier transform for a non-periodic
    signal defined by a Python callable signal_fn(t) → float.

    Freshman picture:
      The continuous FT asks "how much of every possible frequency is in this
      one-time (non-repeating) signal?"  Instead of discrete bins k = 0,1,2…
      you get a smooth curve over all real frequencies.

    This is a Riemann-sum approximation only — educational, not production FFT.
    """
    dt = (t_max - t_min) / max(1, n_t - 1)
    times = [t_min + i * dt for i in range(n_t)]
    values = [float(signal_fn(t)) for t in times]

    df = (f_max - f_min) / max(1, n_f - 1)
    freqs = [f_min + i * df for i in range(n_f)]
    spectrum_c: List[complex] = []
    for f in freqs:
        s = 0.0j
        for t, x in zip(times, values):
            s += x * _cis(-2.0 * math.pi * f * t) * dt
        spectrum_c.append(s)

    mags = [abs(c) for c in spectrum_c]
    return {
        "times": [round(t, 5) for t in times],
        "values": [round(v, 6) for v in values],
        "freqs": [round(f, 5) for f in freqs],
        "magnitudes": [round(m, 6) for m in mags],
        "note": "Riemann-sum continuous FT sketch · educational only",
    }


def gaussian_pulse(t: float, sigma: float = 1.0) -> float:
    """Classic non-periodic test: e^{-t²/(2σ²)}."""
    return math.exp(-(t * t) / (2.0 * sigma * sigma))


def rect_pulse(t: float, width: float = 2.0) -> float:
    """Non-periodic box: 1 inside [-width/2, width/2], else 0."""
    return 1.0 if abs(t) <= width / 2.0 else 0.0


# ---------------------------------------------------------------------------
# Program surface helpers
# ---------------------------------------------------------------------------

def analyze_samples(samples: Sequence[float], top: int = 5) -> Dict[str, Any]:
    """Full DFT report for a sample list."""
    rows = spectrum(samples)
    dom = dominant_frequencies(samples, top=top)
    recon = idft(dft(samples))
    err = sum(abs(a - b) for a, b in zip(samples, recon)) / max(1, len(samples))
    return {
        "n": len(samples),
        "spectrum": rows,
        "dominant": dom,
        "reconstruction_mean_abs_error": round(err, 8),
        "ok": err < 1e-6,
    }


def program_fourier_demo(program=None) -> Dict[str, Any]:
    """Self-contained demo: pure sine + square → spectra."""
    sine = make_sine(64, freq=3.0)
    sq = make_square(64, freq=1.0)
    report = {
        "sine_3": analyze_samples(sine, top=3),
        "square_1": analyze_samples(sq, top=5),
        "continuous_gaussian": continuous_ft_sample(gaussian_pulse, n_t=128, n_f=64),
    }
    if program is not None:
        try:
            program.note_seed(17, "Wave", "fourier_demo")
        except Exception:
            pass
    return report


def smoke() -> bool:
    print("=== FOURIER SMOKE ===")
    r = []
    def rec(n, ok):
        print(f"[{'PASS' if ok else 'FAIL'}] {n}"); r.append(ok)

    # pure sine frequency 3 over 64 samples → peak near k=3
    s = make_sine(64, 3.0)
    dom = dominant_frequencies(s, top=1)
    rec("sine peak near k=3", abs(dom[0]["k"] - 3) <= 1)

    # perfect reconstruction
    X = dft(s)
    recon = idft(X)
    err = sum(abs(a - b) for a, b in zip(s, recon)) / len(s)
    rec("idft reconstruction", err < 1e-9)

    # continuous sketch runs
    cg = continuous_ft_sample(gaussian_pulse, n_t=64, n_f=32)
    rec("continuous FT sketch", len(cg["magnitudes"]) == 32)

    # square wave has odd harmonics
    sq = make_square(64, 1.0)
    doms = dominant_frequencies(sq, top=4)
    ks = {d["k"] for d in doms}
    rec("square odd harmonics present", 1 in ks or 3 in ks)

    print(f"=== {sum(r)}/{len(r)} ===")
    return all(r)


if __name__ == "__main__":
    import sys
    sys.exit(0 if smoke() else 1)
