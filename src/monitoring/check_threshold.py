# monitor/check_threshold.py
# A simple parser that reads the Evidently JSON and exits code accordingly
import json
import sys


with open('drift.json') as f:
    d = json.load(f)


# The structure may vary by Evidently version; try to find dataset_drift flag
# try:
metrics = d.get('metrics', [])
drift = False
drift_value = 0
drift_column = []
for m in metrics:
    r = m.get('value', {})
    if m['metric_id'].find('DriftedColumns')!= -1:
        drift_value = r['share']
        if r['share']>0.5:
            drift = True
    if m['metric_id'].find('ValueDrift')!= -1:
        column_name = ((m['metric_id'].split('column='))[1])[:-1]
        drift_column.append([column_name, r])

    # print(f"{m['metric_id']}: {r}")
    # break
    # if 'dataset_drift' in r and r['dataset_drift']:
    #     drift = True
    #     break
# except Exception:
#     pass


if drift:
    print(f'Drift detected: triggering retrain: {drift_value}')
    print('Column drift:')
    for col in drift_column:
        print(f'{col[0]}: {col[1]}')    
    sys.exit(0) # success -> continue to retrain job
else:
    print(f'No drift detected: skipping retrain: {drift_value}')
    print('Column drift:')
    for col in drift_column:
        print(f'{col[0]}: {col[1]}') 
    sys.exit(78) # custom non-zero to indicate skip