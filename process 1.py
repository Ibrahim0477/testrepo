import re
import glob

import pandas as pd
import matplotlib.pyplot as plt

# Get the last file matching expr by alphabetical sorting
def getRecent(expr):
    return max(
        glob.glob(expr),
        key = lambda x: int(re.search(r'\d+', x).group())
    )

# Inputs
mecmesin_csv = getRecent("C:\\Users\\Ibrahim\\OneDrive - Northeastern University\Desktop\\resisitance testing\\Sensors\\Sensor N\\\Sensor N repeated 10 cycles\\2500*.csv")
keithley_csv = getRecent("C:\\Users\\Ibrahim\\OneDrive - Northeastern University\\Desktop\\resisitance testing\\Sensors\\Sensor N\\Sensor N repeated 10 cycles\\keithley2100*.csv")
event_threshold = 0 # 480 ms
res_cutoff = 5e3

# Detect spans of '0' in the event column and record their indices
def detectEvents(tbl, threshold):
    acc = []
    other = False # Causes iteration on every other group
    # Group by consecutive values in Event column
    for i, g in tbl.groupby(tbl['Event'].ne(tbl['Event'].shift()).cumsum()):
        # Accept span if 'every other' and span is over threshold time
        if other and g['Time'].iloc[-1] - g['Time'].iloc[0] >= threshold:
            acc.append(g.index[0])
        other = not other
    return acc

def main():
    # Load and preprocess data
    tbl = pd.read_csv(mecmesin_csv, skiprows = lambda x: x in [1, 2])
    dmm = pd.read_csv(keithley_csv, header = None)
    dmm_loc = detectEvents(tbl, event_threshold)
    assert len(dmm) == len(dmm_loc)

    tbl.insert(4, 'Resistance', pd.NA)
    tbl['Resistance'] = dmm.set_index([dmm_loc])
    tbl = tbl[tbl['Resistance'] < res_cutoff]

    tbl['Time'] = pd.to_datetime(tbl['Time'], unit = 'm')

    tbl['Force'] = tbl['Force']
    split = tbl['Force'].idxmax()
    tbl_inc = tbl.loc[:split, :]
    tbl_dec = tbl.loc[split:, :]
    
    # Graph data
    fig, ax = plt.subplots()
    tbl_inc.plot(ax = ax, x = 'Force', y = 'Resistance', marker = '>', logy = True)
    tbl_dec.plot(ax = ax, x = 'Force', y = 'Resistance', marker = '<', logy = True)
    ax.legend(['Loading', 'Unloading'])
    ax.set_xlabel('Force (N)')
    ax.set_ylabel('Resistance (Ω)')
    plt.show()
    
if __name__ == '__main__':
    main()
