import pandas as pd
import base64
import io
import json
import dash
from dash import Dash, html, dcc, Input, Output, State
from dash.exceptions import PreventUpdate
from components.query import get_data
from components.graphs import make_hist_plot, make_map, make_pie_plot
from components.divs import get_main_div, get_error_div, get_hist_div, get_map_div

# Fixed style
PRINT_STYLE = {'textAlign': 'center', 'color': 'MidnightBlue', 'margin-bottom' : 10}

# Initialize app/dashboard and set layout
app = Dash(__name__, suppress_callback_exceptions=True)
server = app.server

app.layout = html.Div([
                dcc.Upload(html.Button('Upload Data',
                                    style = {'color': 'MidnightBlue', 
                                            'background-color': 'BlanchedAlmond', 
                                            'border-color': 'MidnightBlue',
                                            'font-size': '16px'}),
                            id = 'upload-data',
                            multiple = False
                            ),
                # Set up memory store with loading indicator, will revert on page refresh
                dcc.Loading(id = 'memory-loading',
                            type = "circle",
                            color = 'DarkMagenta',
                            children = dcc.Store(id = 'memory')),
                html.Hr(),
                
                html.Div(children = [html.H3('Upload data (CSV or XLS) to see distribution statistics.', 
                                              style = PRINT_STYLE),
                                    html.Br(),
                                    html.P(["For further file requirements, please see the ",
                                            html.A("documentation",
                                                    href="https://github.com/Imageomics/telemetry-dashboard/tree/dev#how-it-works",
                                                    target='_blank'),
                                                    "."],
                                              style = PRINT_STYLE)],
                         id = 'output-data-upload')
])

# Data read in and save to memory
@app.callback(
        Output('memory', 'data', allow_duplicate=True),
        Input('upload-data', 'contents'),
        State('upload-data', 'filename'),
        prevent_initial_call = True
)

def parse_contents(contents, filename):
    '''
    Function to read uploaded data.
    '''
    if contents is None:
        raise PreventUpdate
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            df = pd.read_excel(io.BytesIO(decoded))
        else:
            return json.dumps({'error': {'type': 'wrong file type'}})
    except UnicodeDecodeError as e:
        print(e)
        return json.dumps({'error': {'unicode': str(e)}})
    
    except Exception as e:
        print(e)
        return json.dumps({'error': {'other': str(e)}})
    # Check for required columns
    #mapping = True
    features = ['lat', 'lon']
    included_features = list(df.columns)
    for feature in features:
        if feature not in included_features:
            if feature == 'lon':
                if 'long' not in included_features:
                    return json.dumps({'error': {'feature': feature}})
                else:
                    df = df.rename(columns = {"long": "lon"})
                    included_features.remove('long')
                    included_features.append('lon')
            else:
                return json.dumps({'error': {'feature': feature}})
        included_features.sort()
    
    # Check for lat/lon bounds & type 
    try:
        # Check lat and lon within appropriate ranges (lat: [-90, 90], lon: [-180, 180])
        valid_lat = df['lat'].astype(float).between(-90, 90)
        df.loc[~valid_lat, 'lat'] = 'unknown'
        valid_lon = df['lon'].astype(float).between(-180, 180)
        df.loc[~valid_lon, 'lon'] = 'unknown'
    except ValueError as e:
        print(e)
        return json.dumps({'error': {'mapping': str(e)}})

    # get dataset-determined static data:
        # the dataframe and categorical features - processed for map view if mapping is True
        # all possible species, subspecies
        # will likely include categorical options in later instance (sooner)
    processed_df, cat_list = get_data(df, included_features)
    # save data to dictionary to save as json 
    data = {
            'processed_df': processed_df.to_json(date_format = 'iso', orient = 'split'),
            'cat_list': cat_list
            #'mapping': mapping,
        }   
    return json.dumps(data)

# Callback to update processed data if new data uploaded
@app.callback(
        Output('memory', 'data'),
        Input('upload-data', 'contents'),
        State('upload-data', 'filename'),
        prevent_initial_call = True
)
    
def update_output(contents, filename):
    if contents is not None:
        return parse_contents(contents, filename)

# Callback to get main div (histogram, pie chart, and image example options)
@app.callback(
        Output('output-data-upload', 'children'),
        Input('memory', 'data'),
        prevent_initial_call = True
)

def get_visuals(jsonified_data):
    '''
    Function that usese the processed and saved data to get the main div (histogram and pie chart).
    Returns error div if error occurs in upload or essential features are missing.
    '''
    # load saved data
    data = json.loads(jsonified_data)
    if 'error' in data:
        return get_error_div(data['error'])

    # get divs
    hist_div = get_hist_div(data['cat_list'])
    children = get_main_div(hist_div, data['cat_list'])

    return children

# Distribution Section
# Callback to update which options are visible (histogram vs map)
@app.callback(
        Output('dist-options', 'children'),
        Input('dist-view-btn', 'n_clicks'),
        Input('dist-view-btn', 'children'),
        Input('memory', 'data')
)

def update_dist_view(n_clicks, children, jsonified_data):
    '''
    Function to update the upper left distribution options based on selected distribution chart (histogram or map).
    Activates on click to change, defaults to histogram view.

    Parameters:
    -----------
    n_clicks - Number of clicks. 
    children - Label on button, determins which distribution options to show.
    jsonified_data - Saved dictionary of DataFrame, species options, and mapping (boolean on lat/lon availability).

    Returns:
    --------
    hist_div or map_div - The HTML Div corresponding to the selected distribution figure.
    '''
    data = json.loads(jsonified_data)
    if n_clicks == 0 or n_clicks == None:
        return get_hist_div(data['cat_list'])
    if n_clicks > 0:
        if children == "Show Histogram":
            return get_hist_div(data['cat_list'])
        else:
            return get_map_div()

# Callback to update the distribution figure (histogram or map)
@app.callback(
    #dist output
    Output(component_id='dist-plot', component_property='figure'),
    #input x_var
    Input(component_id='x-variable', component_property='value'),
    #input color_by
    Input(component_id='color-by', component_property='value'),
    #input sort_by
    Input(component_id='sort-by', component_property='value'),
    #button information
    Input(component_id='dist-view-btn', component_property='children'),
    # Saved Data
    Input('memory', 'data')
)

def update_dist_plot(x_var, color_by, sort_by, btn, jsonified_data):
    '''
    Function to update distribution figure with either map or histogram based on selections.
    Selection is based on current label of the button ('Map View' or 'Show Histogram'), which updates prior to graph.

    Parameters:
    -----------
    x_var - User-selected variable to plot distribution.
    color_by - User-selected property to color the plot by.
    sort_by - User-selected ordering of bar charts (Alphabetical, Ascending, or Descending).
    btn - Current label of the button ('Map View' or 'Show Histogram').
    jsonified_data - Saved dictionary of DataFrame, species options, and mapping (boolean on lat/lon availability).

    Returns: 
    --------
    fig -  Figure returned from appropriate function call: histogram or map of the distribution of the requested variable.
    '''
    # open dataframe from saved data
    data = json.loads(jsonified_data)
    dff = pd.read_json(data['processed_df'], orient = 'split')
    # get distribution graph based on button value
    if btn == "Show Histogram":
        return make_map(dff, color_by)
    else:
        return make_hist_plot(dff, x_var, color_by, sort_by)

# Pie Section

@app.callback(
    #pie output
    Output(component_id='pie-plot', component_property='figure'),
    #pie input (var)
    Input(component_id='prct-brkdwn', component_property='value'),
    # Saved Data
    Input('memory', 'data')
)

def update_pie_plot(var, jsonified_data):
    '''
    Updates the pie chart of dataset specimens based on user selection of variable to color by.

    Parameters:
    -----------
    var - User-selected categorical variable by which to color.
    jsonified_data - Saved dictionary of DataFrame, species options, and mapping (boolean on lat/lon availability).

    Returns: 
    --------
    fig - Pie chart figure returned from function call: percentage breakdown of `var` samples in the dataset.
    '''
    # open dataframe from saved data
    data = json.loads(jsonified_data)
    dff = pd.read_json(data['processed_df'], orient = 'split')
    return make_pie_plot(dff, var)

if __name__ == '__main__':
    app.run()
