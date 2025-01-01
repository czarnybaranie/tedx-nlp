import pandas as pd
from tqdm import tqdm
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

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