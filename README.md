### Introduction
This python module extracts land use land cover (LULC) type using Copernicus or MODIS LULC products.

### How to use

```python
import pandas as pd
point_filename = pd.read_csv(r'path\to\point\file.csv')
df = extract_gee_lulc(point_filename, 
                  product = 'MODIS/061/MCD12Q1',
                  id_col = 'Site', 
                  start_date = '2020-01-01',
                  end_date = '2020-01-02',
                  bands = ['LC_Type1'], 
                  scale = 10, pad = 0,
                  dest_folder = None)
```
