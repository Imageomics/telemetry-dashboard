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
        fig = px.histogram(df,
                        x = x_var,
                        color = color_by,
                        colorscale = px.colors.qualitative.Bold).update_xaxes(categoryorder = sort_by)

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
    fig = px.scatter_geo(df,
                        lat = df.lat,
                        lon = df.lon,
                        projection = "natural earth", # Note: mapbox doesn't zoom in close enough
                        custom_data = [radius], #, "Species_at_locality", "Subspecies_at_locality"],
                        size = df[radius].to_list(), # number of samples in chosen radius
                        color = radius,
                        color_discrete_sequence = px.colors.qualitative.Bold,
                        title = "Distribution of Samples")
    
    fig.update_geos(fitbounds = "locations",
                    showcountries = True, countrycolor = "Grey",
                    showrivers = True,
                    showlakes = True,
                    showland = True, landcolor = "wheat",
                    showocean = True, oceancolor = "LightBlue")
    
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
        })

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
