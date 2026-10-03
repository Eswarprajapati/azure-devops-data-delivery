import csv,hashlib,json,tempfile,unittest,zipfile,subprocess,sys
from pathlib import Path
from data_job import summarize,run
from tools.build_release import build
ROW={'order_id':'o1','order_date':'2026-01-01','amount_cents':'1000','status':'completed'}
class DeliveryTests(unittest.TestCase):
    def test_completed_and_cancelled(self):
        self.assertEqual(summarize([ROW,dict(ROW,order_id='o2',status='cancelled')])[0]['revenue_cents'],1000)
    def test_duplicate(self):
        with self.assertRaises(ValueError): summarize([ROW,ROW])
    def test_negative(self):
        with self.assertRaises(ValueError): summarize([dict(ROW,amount_cents='-1')])
    def test_invalid_date(self):
        with self.assertRaises(ValueError): summarize([dict(ROW,order_date='2026-02-30')])
    def test_invalid_status(self):
        with self.assertRaises(ValueError): summarize([dict(ROW,status='unknown')])
    def test_failed_input_preserves_previous_output(self):
        with tempfile.TemporaryDirectory() as d:
            source=Path(d)/'bad.csv'; target=Path(d)/'out.csv'; target.write_text('previous')
            with source.open('w',newline='') as f:
                w=csv.DictWriter(f,fieldnames=ROW.keys()); w.writeheader(); w.writerows([ROW,ROW])
            with self.assertRaises(ValueError): run(source,target)
            self.assertEqual(target.read_text(),'previous')
    def test_release_integrity_and_reproducibility(self):
        with tempfile.TemporaryDirectory() as d:
            first=build(Path(d)/'a'); second=build(Path(d)/'b'); self.assertEqual(first,second)
            archive=Path(d)/'a'/'data-job.zip'
            self.assertEqual(first['sha256'],hashlib.sha256(archive.read_bytes()).hexdigest())
            with zipfile.ZipFile(archive) as z: self.assertEqual(z.namelist(),['data_job.py','README.md'])
    def test_packaged_job_runs(self):
        with tempfile.TemporaryDirectory() as d:
            build(d)
            with zipfile.ZipFile(Path(d)/'data-job.zip') as z: z.extractall(Path(d)/'unpacked')
            result=subprocess.run([sys.executable,str(Path(d)/'unpacked/data_job.py'),'data/orders.csv',str(Path(d)/'out.csv')],capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertIn('2500',(Path(d)/'out.csv').read_text())
