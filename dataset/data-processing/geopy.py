import pandas as pd
from tqdm import tqdm
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

import json

# Load the dataset
df = pd.read_csv('FINAL_TEDX_DATASET_2024.csv')

# Extract unique addresses
unique_addresses = df['event_organizer'].unique()

# Initialize geolocator and rate limiter
geolocator = Nominatim(user_agent="ram")
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)

# Create dictionaries to store results
location_dict = {}
lat_dict = {}
longi_dict = {}

# Geocode unique addresses with error handling and checkpoints
for i, addr in enumerate(tqdm(unique_addresses, desc="Geocoding addresses")):
    try:
        location = geocode(addr)
        if location:
            lat_dict[addr] = location.latitude
            longi_dict[addr] = location.longitude
        else:
            lat_dict[addr] = None
            longi_dict[addr] = None
    except Exception as e:
        print(f"Error geocoding {addr}: {e}")
        lat_dict[addr] = None
        longi_dict[addr] = None

    # Save checkpoints every 100 addresses
    if (i + 1) % 100 == 0:
        checkpoint_df = pd.DataFrame({
            'address': list(lat_dict.keys()),
            'latitude': list(lat_dict.values()),
            'longitude': list(longi_dict.values())
        })
        checkpoint_df.to_csv('geocoding_checkpoint.csv', index=False)

# Map results back to the original DataFrame
df['latitude'] = df['event_organizer'].map(lat_dict)
df['longitude'] = df['event_organizer'].map(longi_dict)

# Save final results to CSV
df.to_csv('geocoded_addresses.csv', index=False)

# Extract cities from the dataset

def get_cities(df):
    cities = df[['event_organizer', 'latitude', 'longitude']]
    cities = cities.drop_duplicates()
    cities = cities.dropna(subset=['latitude', 'longitude'])
    return cities

cities = get_cities(df)

# Convert DataFrame to GeoJSON
geojson_data = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [row['longitude'], row['latitude']]
            },
            "properties": {
                "popup": f"<b>{row['event_organizer']}</b>"
            }
        } for _, row in cities.iterrows()
    ]
}

# Optionally, save to a file for reuse
with open("markers.geojson", "w") as f:
    json.dump(geojson_data, f)