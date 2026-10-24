"""Validate public inputs and prepare a local native Power BI runtime copy."""
from pathlib import Path
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from tools.release_qa import validate_data, validate_native

ROOT = Path(__file__).resolve().parent
EXPRESSION = Path('DemandFlow 360.SemanticModel/definition/expressions.tmdl')
TOKEN = '__DEMANDFLOW_DATA_ROOT__'

def prepare(root=ROOT):
    root = Path(root).resolve()
    validate_data(root)
    validate_native(root)
    runtime = root / '.runtime'
    if runtime.is_symlink() or (runtime.exists() and runtime.resolve() != runtime):
        raise ValueError('Unsafe runtime directory: links are not supported.')
    runtime.mkdir(exist_ok=True)
    destination = Path(tempfile.mkdtemp(prefix='session_', dir=runtime))
    native = destination / 'powerbi'
    shutil.copytree(root / 'powerbi', native)
    expression = native / EXPRESSION
    value = (root / 'data/powerbi').as_posix().replace('"', '""')
    text = expression.read_text(encoding='utf-8-sig')
    pattern = r'(?m)^(expression DataRoot = )"' + TOKEN + r'"'
    text, count = re.subn(pattern, lambda m: m[1] + '"' + value + '"', text)
    if count != 1:
        raise ValueError('Expected exactly one canonical DataRoot parameter.')
    expression.write_text(text, encoding='utf-8')
    return native / 'DemandFlow 360.pbip'

def open_desktop(pbip):
    if os.name != 'nt':
        raise OSError('Opening requires Windows and Microsoft Power BI Desktop. Use --prepare-only for validation.')
    try:
        os.startfile(str(pbip))
        return
    except OSError:
        candidates = [Path(os.environ.get('ProgramFiles','')) / 'Microsoft Power BI Desktop/bin/PBIDesktop.exe']
        exe = shutil.which('PBIDesktop.exe')
        if exe:
            candidates.insert(0, Path(exe))
        for candidate in candidates:
            if candidate.is_file():
                subprocess.Popen([str(candidate), str(pbip)])
                return
        raise OSError('Power BI Desktop/PBIP association not found. Install current Microsoft Power BI Desktop, then retry. No refresh was performed.')

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepare-only', action='store_true', help='Validate and prepare without opening Desktop')
    args = parser.parse_args()
    try:
        pbip = prepare()
        print('Validated public data. Runtime project:', pbip)
        if not args.prepare_only:
            open_desktop(pbip)
            print('Open request sent. In Desktop choose Home > Refresh; wait for completion. Opening is not proof of successful refresh.')
        else:
            print('PREPARE PASS. Desktop refresh and visual interaction were not tested by this command.')
        return 0
    except (OSError, ValueError, AssertionError, KeyError) as exc:
        print('ERROR:', exc, file=sys.stderr)
        return 1

if __name__ == '__main__':
    raise SystemExit(main())
