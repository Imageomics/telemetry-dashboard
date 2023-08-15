# Helper functions for Dashboard

PRINT_STYLE = {"color": "MidnightBlue"}

def get_data(df, features):
    '''
    Function to read in DataFrame and perform required manipulations: 
        - fill null values in required columns with 'unknown'
        - add 'lat-lon' and `Samples_in_km`columns for .1 through .5 km radius.
        - make list of categorical columns.

    Parameters:
    -----------
    df - DataFrame of the data to visualize.
    features - List of features (columns) included in the DataFrame.
            
    Returns:
    --------
    df - DataFrame with added 'lat-lon' column and columns indicating number of samples collected at each lat-lon pair.
    cat_list - List of categorical variables for RadioItems (pie chart and map).

    '''
    df = df.copy()
    df = df.fillna('unknown')
    features.append('locality')

    # Fixed distance for radii around lat/lon (in km)
    bounding_radii = {'half_km': .5,
                      '4-10_km': .4,
                      '3-10_km': .3,
                      '2-10_km': .2,
                      'tenth_km': .1}
    
    # lat and lon must be in dataset, so process locality information
    df['lat-lon'] = df['lat'].astype(str) + '|' + df['lon'].astype(str)

    for key in bounding_radii.keys():
        df[key] = get_points_in_radius(df[['lat', 'lon', 'lat-lon']], bounding_radii[key])

    #df["Samples_at_locality"] = df['lat-lon'].map(df['lat-lon'].value_counts()) # will duplicate if multiple views of same sample

    """  # Count and record number of species and subspecies at each lat-lon
    for lat_lon in df['lat-lon']:
        species_list = ['{}'.format(i) for i in df.loc[df['lat-lon'] == lat_lon]['Species'].unique()]
        subspecies_list = ['{}'.format(i) for i in df.loc[df['lat-lon'] == lat_lon]['Subspecies'].unique()]
        df.loc[df['lat-lon'] == lat_lon, "Species_at_locality"] = ", ".join(species_list)
        df.loc[df['lat-lon'] == lat_lon, "Subspecies_at_locality"] = ", ".join(subspecies_list) 
    """

    if 'locality' not in df.columns:
        df['locality'] = df['lat-lon'] # contains "unknown" if lat or lon null

    new_features = ['lat-lon', 'half_km', '4-10_km', '3-10_km', '2-10_km', 'tenth_km']
    for feature in new_features:
        features.append(feature)

    # Dictionary of categorical values for graphing options  
    # Will likely choose to calculate and return this in later instance    
    cat_list = []
    for col in features[:-6]:
        cat_list.append({'label': col, 'value': col})

    return df[features], cat_list

def get_points_in_radius(df, radius):
    '''
    Function to find points within [radius] of latitude and longitude.

    Parameters:
    -----------
    df - DataFrame with lat/long values
    radius - Float. Radius within which to look (km).

    Returns:
    --------
    num_samples - Number of samples within the given radius of the point.

    '''
    # Convert distance to degrees (approx)
    # Use approximate conversion at equator from US Naval Academy: https://www.usna.edu/Users/oceano/pguth/md_help/html/approx_equivalents.htm
    # Approx 111 km per degree near equator (for both lat and lon)
    rad_deg = radius/111 
    pts_per_lat_lon = []
    print(radius)

    for point in df['lat-lon']:
        temp = df.loc[df['lat-lon'] == point]
        # Define boundary square around the coordinates
        min_lat = temp.lat.values[0] - rad_deg
        max_lat = temp.lat.values[0] + rad_deg
        min_lon = temp.lon.values[0] - rad_deg
        max_lon = temp.lon.values[0] + rad_deg

        filtered_df = df.loc[df['lat'] > min_lat]
        filtered_df = filtered_df.loc[filtered_df['lat'] < max_lat]
        filtered_df = filtered_df.loc[filtered_df['lon'] > min_lon]
        filtered_df = filtered_df.loc[filtered_df['lon'] < max_lon]

        pts_per_lat_lon.append(len(filtered_df))
   
    return pts_per_lat_lon
