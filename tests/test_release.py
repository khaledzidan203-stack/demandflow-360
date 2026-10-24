"""Public release regression, including portable/hostile-input cases."""
from pathlib import Path
import csv
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from tools.release_qa import ROOT, digest, validate_data, validate_native, publication_scan
from tools.reproduce import reproduce
from launch_powerbi import prepare

class ReleaseTests(unittest.TestCase):
    def test_public_data(self):
        self.assertEqual(len(validate_data()['fact_observed']),2688)

    def test_python_sql_independent_parity(self):
        self.assertEqual(reproduce()['group_rows_reconciled'],145)

    def test_native_structure_bindings_and_navigation(self):
        self.assertEqual(validate_native()['navigation_targets'],10)

    def test_publication_scan(self):
        self.assertGreater(publication_scan(),100)

    def test_readme_links_and_screenshots(self):
        import re
        text=(ROOT/'README.md').read_text(encoding='utf-8')
        links=re.findall(r'\]\(([^)]+)\)',text)
        images=[x for x in links if x.startswith('screenshots/')]
        self.assertEqual(len(images),6)
        for target in links:
            if '://' not in target and not target.startswith('#'):
                self.assertTrue((ROOT/target.split('#')[0]).is_file(),target)
        for name in images:
            self.assertTrue((ROOT/name).read_bytes().startswith(b'\x89PNG\r\n\x1a\n'))

    def test_portable_unicode_unrelated_cwd_repeat_and_immutability(self):
        with tempfile.TemporaryDirectory(prefix='DemandFlow 360 QA ') as temp:
            copy=Path(temp)/'Portable project \u062a\u062d\u0644\u064a\u0644'
            shutil.copytree(ROOT,copy,ignore=shutil.ignore_patterns('.git','.runtime','outputs','__pycache__'))
            before={p.relative_to(copy).as_posix():digest(p) for p in copy.rglob('*') if p.is_file()}
            for _ in range(2):
                run=subprocess.run([sys.executable,str(copy/'launch_powerbi.py'),'--prepare-only'],cwd=Path(temp),capture_output=True,text=True,encoding='utf-8',env={**__import__('os').environ,'PYTHONIOENCODING':'utf-8'})
                self.assertEqual(run.returncode,0,run.stderr)
            expressions=list((copy/'.runtime').glob('session_*/powerbi/*SemanticModel/definition/expressions.tmdl'))
            self.assertEqual(len(expressions),2)
            self.assertEqual(expressions[0].read_bytes(),expressions[1].read_bytes())
            self.assertIn((copy/'data/powerbi').as_posix(),expressions[0].read_text())
            self.assertNotIn(str(ROOT),expressions[0].read_text())
            for name,sha in before.items(): self.assertEqual(digest(copy/name),sha,name)
            self.assertEqual(reproduce(copy)['totals']['sales_units'],5272)

    def test_missing_csv_fails_before_runtime_write(self):
        with tempfile.TemporaryDirectory() as temp:
            copy=Path(temp)/'missing';shutil.copytree(ROOT,copy,ignore=shutil.ignore_patterns('.git','.runtime','outputs','__pycache__'))
            (copy/'data/powerbi/dim_day.csv').rename(copy/'missing_day.csv')
            with self.assertRaisesRegex(ValueError,'Missing required CSV'):prepare(copy)
            self.assertFalse((copy/'.runtime').exists())

    def test_schema_and_checksum_fail_closed(self):
        for mutation,expected in [('schema','schema'),('checksum','checksum')]:
            with self.subTest(mutation=mutation),tempfile.TemporaryDirectory() as temp:
                copy=Path(temp)/'corrupt';shutil.copytree(ROOT,copy,ignore=shutil.ignore_patterns('.git','.runtime','outputs','__pycache__'))
                p=copy/'data/powerbi/fact_observed.csv'
                text=p.read_text();text=text.replace('gross_sales_qty','unexpected_private_column',1) if mutation=='schema' else text+'\n'
                p.write_text(text)
                with self.assertRaisesRegex(ValueError,expected):prepare(copy)
                self.assertFalse((copy/'.runtime').exists())

    def test_native_tamper_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            copy=Path(temp)/'native';shutil.copytree(ROOT,copy,ignore=shutil.ignore_patterns('.git','.runtime','outputs','__pycache__'))
            p=copy/'powerbi/DemandFlow 360.SemanticModel/definition/expressions.tmdl';p.write_text('invalid')
            with self.assertRaisesRegex(ValueError,'native file'):prepare(copy)
            self.assertFalse((copy/'.runtime').exists())

if __name__=='__main__':unittest.main()
