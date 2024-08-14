# Google Reviews Mapper

Use the script in this repo to access Google Maps' Places API, Nearby Search endpoint to retrieve a list of establishments and review data around an area.

## Usage

1. Create a Google Cloud account.

2. Setup a billing account.

3. Enable the Google Maps Nearby Search API and retrieve an API key.

4. Setup Python virtual environment:

```
# Windows (Powershell)

python -m venv venv
\venv\Scripts\activate
pip install -r requirements.txt
```

```
# Mac/Linux (bash)

python -m venv venv
source ./venv/bin/activate
pip install -r requirements.txt
```

5. Run the `get_restaurants.py` script, replacing `API_KEY` with your own key. Adjust any function arguments as desired.

6. Visualize the data in Python or in another tool for mapping (I've used Tableau for my own examples)

## To do

1. Refactor the code to be command line executable

2. Make generic for searches of all types of establishments

3. Test with the Nearby Search (New) API endpoint and compare results

4. Optimize the grid creation to spread points over a given city/municipality.

5. Add error handling