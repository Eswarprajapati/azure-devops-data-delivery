"""Validate a daily sales partition and write a deterministic revenue CSV."""
import argparse, csv, os, tempfile
from pathlib import Path
from datetime import date

def summarize(rows):
    totals={}; seen=set()
    for row in rows:
        oid=row['order_id'].strip(); day=date.fromisoformat(row['order_date']).isoformat()
        if not oid or oid in seen: raise ValueError('Missing or duplicate order_id')
        seen.add(oid)
        amount=int(row['amount_cents'])
        if amount<0: raise ValueError('Negative amount')
        if row['status'] not in ('completed','cancelled'): raise ValueError('Invalid status')
        totals.setdefault(day,0)
        if row['status']=='completed': totals[day]+=amount
    return [{'order_date':day,'revenue_cents':value} for day,value in sorted(totals.items())]

def run(source,target):
    with open(source,newline='',encoding='utf-8') as f: output=summarize(csv.DictReader(f))
    target=Path(target); target.parent.mkdir(parents=True,exist_ok=True)
    fd,name=tempfile.mkstemp(dir=target.parent,suffix='.tmp')
    try:
        with os.fdopen(fd,'w',newline='',encoding='utf-8') as f:
            writer=csv.DictWriter(f,fieldnames=['order_date','revenue_cents'])
            writer.writeheader(); writer.writerows(output)
        os.replace(name,target)
    finally:
        if os.path.exists(name): os.unlink(name)
    return output

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('source'); p.add_argument('target'); a=p.parse_args()
    print(run(a.source,a.target))
