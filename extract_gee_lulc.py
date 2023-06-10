def extract_gee_lulc(point_filename, 
                 product='ESA/WorldCover/v100', 
                 id_col='Site', 
                 start_date='2020-01-01',
                 end_date='2020-01-02',
                 bands=['Map'], 
                 scale=10, pad=0,
                 dest_folder=None):
    
    '''
    This function extracts land use land cover data from Google Earth Engine for a given set of points. 
    Uses the function 'gee_point_extract' from the script 'gee_extract_multi_point_data.py' available at github.com/akhi9661/gee_extract_multi_point_data.

    Parameters: 
        point_filename (str): The path to the pandas dataframe containing the points. Must contain columns named 'lat' and 'lon'.
        product (str): The name of the land use land cover product to be extracted. The default is 'ESA/WorldCover/v100'. Other option is 'MODIS/061/MCD12Q1'.
        id_col (str): The name of the column containing the site IDs. The default is 'Site'.
        start_date (str): The start date of the time period for which the data is to be extracted. The default is '2020-01-01'. Format is 'YYYY-MM-DD'.
        end_date (str): The end date of the time period for which the data is to be extracted. The default is '2020-01-02'. Format is 'YYYY-MM-DD'.
        bands (list): The list of bands to be extracted. The default is ['Map']. For 'MODIS/061/MCD12Q1', the options are ['LC_Type1'] and ['LC_Type2'].
        scale (int): The scale at which the data is to be extracted. The default is 10. Generally, matches the native resolution of the product.
        pad (float): The padding to be used for the extraction. The default is 0.9. Units are in km. 
        dest_folder (str): The path to the folder where the output csv file is to be saved. The default is None. If None, the file is saved in the current working directory.

    Returns:
        A pandas dataframe containing the extracted data. 

    '''

    import requests, os, pandas as pd
    from io import StringIO

    if dest_folder is None:
        opf = os.path.join(os.getcwd(), f'{product.split("/")[-1]}_{start_date}_{end_date}.csv')
    else:
        opf = os.path.join(dest_folder, f'{product.split("/")[-1]}_{start_date}_{end_date}.csv')

    github_link = "https://raw.githubusercontent.com/akhi9661/gee_extract_multi_point_data/main/gee_point_extract.py"
    response = requests.get(github_link)
    gee_extract = response.text
    script_file = StringIO(gee_extract)
    exec(script_file.read())

    function_name = "gee_point_extract"
    
    if product == 'ESA/WorldCover/v100':
        mapping_df = pd.DataFrame({'Value': [10, 20, 30, 40, 50, 60, 70, 80, 90, 95, 100],
                                   'Description': ['Tree cover', 'Shrubland', 'Grassland', 'Cropland', 
                                                   'Built-up', 'Bare / sparse vegetation', 'Snow and ice', 
                                                   'Permanent water bodies', 'Herbaceous wetland', 'Mangroves', 
                                                   'Moss and lichen']})
        start_date = '2020-01-01'
        end_date = '2020-01-02'
        scale = 10
        pad = 0.9

    if product == 'MODIS/061/MCD12Q1':
        if bands[0] == 'LC_Type1':
            mapping_df = pd.DataFrame({'Value': list(range(1, 18)),
                                       'Description': ['Evergreen Needleleaf Forests', 'Evergreen Broadleaf Forests', 
                                                       'Deciduous Needleleaf Forests', 'Deciduous Broadleaf Forests', 
                                                       'Mixed Forests', 'Closed Shrublands', 'Open Shrublands', 
                                                       'Woody Savannas', 'Savannas', 'Grasslands', 'Permanent Wetlands',
                                                       'Croplands', 'Urban and Built-up Lands', 'Cropland/Natural Vegetation Mosaics', 
                                                       'Permanent Snow and Ice', 'Barren', 'Water Bodies']})
            start_date = '2020-01-01'
            end_date = '2020-01-02'
            scale = 500
            pad = 0

        if bands[0] == 'LC_Type2':
            mapping_df = pd.DataFrame({'Value': list(range(0, 16)),
                                       'Description': ['Water Bodies', 'Evergreen Needleleaf Forests', 'Evergreen Broadleaf Forests', 
                                                       'Deciduous Needleleaf Forests', 'Deciduous Broadleaf Forests', 
                                                       'Mixed Forests', 'Closed Shrublands', 'Open Shrublands', 
                                                       'Woody Savannas', 'Savannas', 'Grasslands', 'Permanent Wetlands',
                                                       'Croplands', 'Urban and Built-up Lands', 'Cropland/Natural Vegetation Mosaics', 
                                                       'Non-Vegetated Lands']})
            start_date = '2020-01-01'
            end_date = '2020-01-02'
            scale = 500
            pad = 0

    if function_name in locals():
        df = locals()[function_name](point_filename, product=product, 
                                     start_date=start_date,
                                     end_date=end_date,
                                     id_col='Site', pad=pad,
                                     bands=bands, 
                                     scale=scale, dest_folder=None)
    else:
        print(f"The function '{function_name}' is not defined in the script.")

    df[id_col] = df[id_col].astype('category')
    df[bands[0]] = df[bands[0]].astype('category')

    map_counts = df[bands[0]].value_counts()
    site_map_counts = df.groupby(id_col)[bands[0]].count()

    new_df = pd.DataFrame(columns=[id_col, 'lat', 'lon', bands[0], 'Class'])

    for site in df[id_col].unique():
        site_data = df[df[id_col] == site]
        site_data = df[df[id_col] == site]
        site_map_counts = site_data[bands[0]].value_counts()

        majority_value = site_map_counts.idxmax()
        site_class_data = pd.DataFrame({id_col: [site] * len(site_map_counts),
                                        'lat': site_data['latitude'].values[0],  # Append latitude
                                        'lon': site_data['longitude'].values[0],  # Append longitude
                                        bands[0]: site_map_counts.index,
                                        'Class': [majority_value] * len(site_map_counts)})
        new_df = new_df.append(site_class_data, ignore_index=True)

    new_df = new_df.drop_duplicates(subset=['Site'])

    merged_df = new_df.merge(mapping_df, left_on='Class', right_on='Value', how='left')
    merged_df['Class Name'] = merged_df['Description'].where(pd.notnull(merged_df['Description']), '')
    merged_df.drop(['Value', 'Description'], axis=1, inplace=True)
    merged_df.to_csv(opf, index=False)

    return merged_df
