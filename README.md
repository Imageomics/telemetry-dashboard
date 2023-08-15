# Telemetry Dashboard 
Prototype data dashboard for analyzing telemetry data.


## How it works

For full dashboard functionality, upload a CSV or XLS file with the following columns: 
- `lat`*: Latitude at which image was taken or specimen was collected.
- `lon`*: Longitude at which image was taken or specimen was collected.


***Note:** 
- `lat` and `lon` columns are not required to utilize the dashboard, but there will be no map view if they are not included.

## Running Dashboard

Create and activate a new (python) virtual environment. 
Then install the required packages (if using `conda`, first run `conda install pip`):

``` 
pip install -r requirements.txt 
```

and run 

```
python dashboard.py
```

Then navigate to [http://127.0.0.1:8050/](http://127.0.0.1:8050/) in your browser to see the graphs.

## Running with Docker
To run the dashboard in a more scalable manner a Dockerfile is provided.
This container uses [gunicorn](https://gunicorn.org/) to support more users at the same time.
Building and running the container requires that [docker](https://www.docker.com/) is installed.

### Building the container
```
docker build -t dashboard .
```

### Running the container
To deploy the dashboard with 6 workers run the following command:
```
docker run --env BACKEND_WORKERS=6 -p 5000:5000 -it dashboard
```
Then open the following URL <http://0.0.0.0:5000/>.


## Preview
Note: These previews are of the original animal-focused dashboard. The Image selector is not included here and the interface is flexible.

### Histogram View
![image](dashboard_preview_hist.png)


### Map View
![image](dashboard_preview_map.png)


## Testing

Note: Tests are not currently applicable.

### Test Requirements
The testing suite requires [Dash Testing](https://dash.plotly.com/testing) and [pytest-mock](https://pypi.org/project/pytest-mock/), which can be installed in your python environment by running:
```
pip install dash\[testing] pytest-mock
```

### Running Tests

Within your python environment run the following command to run all tests:
```
pytest
```
