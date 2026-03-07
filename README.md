# GeoLocate Tool

A Python-based IP geolocation utility that resolves domain names and queries geographical location data for IP addresses using MaxMind's GeoLite2-City database.

## Features

- **URL to IP Resolution** - Automatically translates domain names to IP addresses
- **Geolocation Lookup** - Queries detailed location information for any IP address
- **Auto-Dependency Installation** - Automatically installs the `geoip2` library if missing
- **Auto-Database Download** - Downloads GeoLite2-City database automatically if not present
- **Detailed Location Data** - Returns comprehensive information including:
  - Country (ISO code and name)
  - City name
  - Postal code
  - Latitude and Longitude coordinates
  - Time zone
  - City subdivisions
- **Custom Database Support** - Option to use your own .mmdb database file

## Requirements

- Python 3.6 or higher
- `geoip2` library (auto-installed if missing)
- MaxMind GeoLite2-City database (auto-downloaded if missing)
- Internet connection for initial setup
- `sudo` access may be required for system-wide database installation

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/jack9038/Tools.git
   cd Tools
2.python3 --version
3.python3 GeoLocate.py --help
4.python3 GeoLocate.py --url example.com
