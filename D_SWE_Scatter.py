##Points=vector 
from qgis.core import *
from PyQt4.QtCore import *
import matplotlib.pyplot as plt
import numpy as np 
 
inLayer = processing.getObject(Points)

delta_list = [f['D_SWE_OM'] for f in inLayer.selectedFeatures()]
station_id = [f['STATION_ID'] for f in inLayer.selectedFeatures()]
ob_swe = [f['OB_SWE'] for f in inLayer.selectedFeatures()]

delta_abs = [abs(i) for i in delta_list]

idx_max_delta = delta_abs.index(max(delta_abs))

std_dev = np.std(delta_list, ddof=1)
x = list(range(0, len(delta_list), 1))

plt.scatter(x, delta_list, color='gray', marker='.')
plt.plot([0,max(x)], [0,0], color='black', linewidth=0.5)

if max(delta_abs) > 0.03:
    plt.plot([0, max(x)], [0.03, 0.03], color='green', linewidth=0.5)
    plt.plot([0, max(x)], [-0.03, -0.03], color='green', linewidth=0.5)

plt.plot([0,max(x)], [std_dev, std_dev], color='red', linewidth=0.5)
plt.plot([0,max(x)], [-1 * std_dev, -1 * std_dev], color='blue', linewidth=0.5)
plt.ylabel('Delta SWE (Obs - SNODAS) (meters)')
plt.text(x[idx_max_delta]+1, delta_list[idx_max_delta], station_id[idx_max_delta])

plt.title(str(round(sum(ob_swe)/len(ob_swe), 3)) + ' Meters of Snow Depth (average)')

plt.show()