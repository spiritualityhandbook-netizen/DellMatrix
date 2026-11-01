"""Director boundary probes; run from repo root. Synthetic owners only.
Reports observations, not a production regression suite or certification tool.
"""
import json
import os
import platform
import uuid
from types import SimpleNamespace
from unittest.mock import patch
from form.step8_transactions_test import _program, _run, _cleanup, _msgs
from form.dell_matrix import exchange
from form import regress

print(json.dumps({'python': platform.python_version(), 'platform': platform.platform(),
                  'pid': os.getpid(), 'self_starttime': regress._proc_starttime(os.getpid())}))
with patch.object(exchange, '_compensate_import', return_value=(True, [])), \
     patch.object(exchange, '_clear_import_journal', return_value=False):
    err = exchange._fail_import(SimpleNamespace(owner='synthetic'), {}, 'p', 'final_save', OSError('synthetic'))
    print('journal deletion failure receipt:', json.dumps(err.details, sort_keys=True))
owner = 'dir_boundary_' + uuid.uuid4().hex[:12]
try:
    p = _program(owner)
    try:
        result = _run(p, '13[Loop] :: ²')
        print('unicode Loop:', result.get('ok'), result.get('error'))
    except Exception as exc:
        print('unicode Loop raised:', type(exc).__name__, str(exc))
    for seed in ['93[Try]', '86[Delete] :: absent', '94[Catch]', '94[Catch]']:
        result = _run(p, seed)
        print(seed, result.get('ok'), _msgs(result))
finally:
    _cleanup(owner)
