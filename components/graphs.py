import plotly.express as px

def make_hist_plot(df, x_var, color_by, sort_by):
    '''
    Generates interactive histogram of selected variable, with option of properties to color by and order in which to sort.
    
    Parameters:
    -----------
    df - DataFrame of specimens.
    x_var - Variable to plot distribution.
    color_by - Property to color the plot by.
    sort_by - Ordering of bar charts (Alphabetical, Ascending, or Descending).

    Returns: 
    --------
    fig - Histogram of the distribution of the requested variable.
    '''
    if sort_by == 'alpha':
        df['sorted'] = df[x_var].astype(str)
        df = df.sort_values('sorted')
        fig = px.bar(df,
                     x = x_var,
                        color = color_by,
                        color_continuous_scale = px.colors.sequential.Plasma)
    else:
        fig = px.bar(df,
                        x = x_var,
                        color = color_by,
                        color_continuous_scale = px.colors.sequential.Plasma).update_xaxes(categoryorder = sort_by)

    fig.update_layout(title = {'text': f'Distribution of {x_var} Colored by {color_by}'},
                      title_font_size = 20,
                      legend_font_size = 10,
                      margin = {
                            'l': 30,
                            'r': 20,
                            't': 35,
                            'b': 20
                        })

    return fig

def make_map(df, color_by):
    '''
    Generates interactive map of species and subspecies by location.
    
    Parameters:
    -----------
    df - DataFrame of specimens.
    color_by - Selected categorical variable by which to color.

    Returns: 
    --------
    fig - Map of their locations.
    '''
    bounding_radii = {.5: 'half_km',
                      .4: '4-10_km',
                      .3: '3-10_km',
                      .2: '2-10_km',
                      .1: 'tenth_km'}
    radius = bounding_radii[color_by]
    df = df.copy()
    # only use entries that have valid lat & lon for mapping
    df = df.loc[df['lat-lon'].str.contains('unknown') == False]
    
    fig = px.scatter_mapbox(df,
                            lat = "lat",
                            lon = "lon",
                            #projection = "natural earth",
                            custom_data = [radius], #, "Species_at_locality", "Subspecies_at_locality"],
                            size = df[radius].to_list(), # number of samples in chosen radius
                            color = radius,
                            color_discrete_sequence = px.colors.qualitative.Bold,
                            title = "Distribution of Samples",
                            zoom = 2,
                            mapbox_style = "stamen-terrain",
                            height = 700)
    
    fig.update_traces(hovertemplate = 
                        "Latitude: %{lat}<br>"+
                        "Longitude: %{lon}<br>" +
                        "Samples within chosen radius: %{customdata[0]}<br>"
    )

    fig.update_layout(
        title_font_size = 20,
        legend_font_size = 10,
        margin = {
            'l': 20,
            'r': 20,
            't': 35,
            'b': 20
        },
        mapbox_layers = [{
            "below": "traces",
            "sourcetype": "raster",
            #"sourceattribution": "United States Geological Survey",
            #"source": [ "https://basemap.nationalmap.gov/arcgis/rest/services/USGSImageryOnly/MapServer/tile/{z}/{y}/{x}"]
            # Switches to white map when you get too close
            # This one can zoom closer and has more detail (trees), but get grey "Map data not yet available" when you get too close
            "sourceattribution": "Esri, Maxar, Earthstar Geographics, and the GIS User Community",
            "source": ["https://services.arcgisonline.com/arcgis/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"]
            # Usage and Licensing (ArcGIS World Imagery): https://services.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer
            # Style: https://roblabs.com/xyz-raster-sources/styles/arcgis-world-imagery.json
        }])

    return fig

def make_pie_plot(df, var):
    '''
    Generates interactive pie chart of dataset specimens with option of properties to color by.

    Parameters:
    -----------
    df - DataFrame of specimens.
    var - Selected categorical variable by which to color.
    
    Returns: 
    --------
    fig - Pie chart of the percentage breakdown of the `var` samples in the dataset.
    '''
    pie_fig = px.pie(df,
                names = var,
                color_discrete_sequence = px.colors.qualitative.Bold)
    pie_fig.update_traces(textposition = 'inside', textinfo = 'percent+label')

    pie_fig.update_layout(title = {'text': f'Percentage Breakdown of {var}'},
                          title_font_size = 20,
                          legend_font_size = 10,
                          margin = {
                                'l': 20,
                                'r': 20,
                                't': 35,
                                'b': 20
                            })

    return pie_fig
