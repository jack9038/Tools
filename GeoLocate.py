#!/usr/bin/python

import sys
import socket
import os
import glob

try:
    import geoip2.database
    print('[DONE] geoip2 imported successfully')
except ImportError:
    print('[!] Failed to import geoip2')
    try:
        choice = input('[*] Attempt to Auto-install geoip2? [y/N] ')
    except KeyboardInterrupt:
        print('\n[!] User Interrupted Choice')
        sys.exit(1)

    if choice.strip().lower()[0] == 'y':
        print('[*] Attempting to Install geoip2...')
        sys.stdout.flush()
        try:
            import subprocess
            result = subprocess.run(
                ['pip3', 'install', 'geoip2', '--break-system-packages'],
                capture_output=True, text=True
            )
            if result.returncode != 0:
                print(result.stderr)
                raise Exception('pip install failed')
            import geoip2.database
            print('[DONE]')
        except Exception as e:
            print(f'[FAIL] {e}')
            sys.exit(1)
    elif choice.strip().lower()[0] == 'n':
        print('[*] User Denied Auto-Install')
        sys.exit(1)
    else:
        print('[!] Invalid Decision')
        sys.exit(1)


class Locator(object):
    def __init__(self, url=False, ip=False, datfile=False):
        self.url = url
        self.ip = ip
        self.datfile = datfile
        self.target = ''

    def find_mmdb(self):
        """Dynamically find the .mmdb file regardless of date-versioned folder name."""
        # Check user-specified datfile first
        if self.datfile and os.path.isfile(self.datfile):
            return self.datfile

        # Search common locations
        search_paths = [
            '/usr/share/GeoIP/**/*.mmdb',
            '/usr/local/share/GeoIP/**/*.mmdb',
            './**/*.mmdb',
        ]
        for pattern in search_paths:
            matches = glob.glob(pattern, recursive=True)
            if matches:
                return matches[0]

        return None

    def check_database(self):
        mmdb = self.find_mmdb()
        if mmdb:
            print(f'[*] Database found: {mmdb}')
            return

        print('[!] No GeoIP database detected')
        try:
            choice = input('[*] Attempt to Auto-Download Database? [y/N] ')
        except KeyboardInterrupt:
            print('\n[!] User Interrupted Choice')
            sys.exit(1)

        if choice.strip().lower()[0] != 'y':
            print('[!] User Denied Auto-Install')
            sys.exit(1)

        print('[*] Attempting to Download Database...')
        sys.stdout.flush()

        geoip_dir = '/usr/share/GeoIP'
        if not os.path.isdir(geoip_dir):
            try:
                os.makedirs(geoip_dir)
            except PermissionError:
                print('[!] Permission denied creating /usr/share/GeoIP. Try running with sudo.')
                sys.exit(1)

        try:
            import subprocess
            tar_gz_path = os.path.join(geoip_dir, 'GeoLite2-City.tar.gz')

            print('[*] Downloading...')
            result = subprocess.run([
                'sudo', 'wget', '--content-disposition',
                '--user=1309143',
                '--password=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',
                '-O', tar_gz_path,
                'https://download.maxmind.com/geoip/databases/GeoLite2-City/download?suffix=tar.gz'
            ])
            if result.returncode != 0:
                raise Exception('wget failed')
            print('[DONE] Download complete')
        except Exception as e:
            print(f'[FAIL] Failed to Download Database: {e}')
            sys.exit(1)

        try:
            print('[*] Extracting...')
            import subprocess
            result = subprocess.run([
                'sudo', 'tar', '-xvf', tar_gz_path, '-C', geoip_dir
            ])
            if result.returncode != 0:
                raise Exception('tar extraction failed')
            print('[DONE] Extraction complete')
        except Exception as e:
            print(f'[FAIL] Failed to Decompress Database: {e}')
            sys.exit(1)

        # Verify it now exists
        mmdb = self.find_mmdb()
        if not mmdb:
            print('[!] Database still not found after extraction. Check the extracted folder.')
            sys.exit(1)

        print(f'[*] Database ready: {mmdb}')

    def query(self):
        # Resolve URL to IP if needed
        if self.url:
            print(f'[*] Translating {self.url}...')
            sys.stdout.flush()
            try:
                self.target = socket.gethostbyname(self.url)
                print(f'[*] Resolved to: {self.target}')
            except Exception:
                print('\n[!] Failed to Resolve URL')
                return
        else:
            self.target = self.ip

        # Find mmdb
        mmdb = self.find_mmdb()
        if not mmdb:
            print('[!] No database file found. Run check_database() first.')
            return

        try:
            print(f'\n[*] Querying records for {self.target}...\n')
            with geoip2.database.Reader(mmdb) as reader:
                response = reader.city(self.target)

                print(f'  Country ISO Code : {response.country.iso_code}')
                print(f'  Country Name     : {response.country.name}')
                print(f'  City Name        : {response.city.name}')
                print(f'  Postal Code      : {response.postal.code}')
                print(f'  Latitude         : {response.location.latitude}')
                print(f'  Longitude        : {response.location.longitude}')
                print(f'  Time Zone        : {response.location.time_zone}')
                print(f'City subdivisions: {response.subdivisions.most_specific}')

            print('\n[*] Query Complete!')

        except geoip2.errors.AddressNotFoundError:
            print(f'\n[!] IP address {self.target} not found in database')
        except FileNotFoundError:
            print(f'\n[!] Database file not found at: {mmdb}')
        except Exception as e:
            print(f'\n[!] Failed to Retrieve Records')
            print(f'    Error: {type(e).__name__}: {e}')


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='IP Geolocation Tool')
    parser.add_argument('--url', help='Locate an IP based on a URL',
                        action='store', default=False, dest='url')
    parser.add_argument('-t', '--target', help='Locate the specified IP',
                        action='store', default=False, dest='ip')
    parser.add_argument('--dat', help='Custom .mmdb database filepath',
                        action='store', default=False, dest='datfile')
    args = parser.parse_args()

    if ((args.url and args.ip) or (not args.url and not args.ip)):
        parser.error('Specify either --url or -t/--target, not both or neither')

    try:
        locator = Locator(url=args.url, ip=args.ip, datfile=args.datfile)
        locator.check_database()
        locator.query()
    except KeyboardInterrupt:
        print('\n\n[!] Unexpected User Interrupt')
        sys.exit(1)