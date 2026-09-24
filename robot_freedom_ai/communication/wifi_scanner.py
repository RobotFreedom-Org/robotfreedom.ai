# Source - https://stackoverflow.com/a/79941032
# Posted by ahmed farag
# Retrieved 2026-09-02, License - CC BY-SA 4.0

#!/usr/bin/env python3
"""
WiFi Scanner - Cross-platform WiFi network scanner
Requires: scapy (pip install scapy)
"""

import platform
import subprocess
import re
import threading
import time
from collections import defaultdict
import json

class WiFiScanner:
    def __init__(self):
        self.system = platform.system().lower()
        self.networks = defaultdict(list)
        self.running = False
        
    def scan_windows(self):
        """Windows WiFi scan using netsh"""
        try:
            result = subprocess.run(['netsh', 'wlan', 'show', 'profiles'], 
                                  capture_output=True, text=True, encoding='cp437')
            profiles = re.findall(r'All User Profile\s*:\s*(.+)', result.stdout)
            
            networks = []
            for profile in profiles:
                profile = profile.strip()
                # Get signal strength
                signal_result = subprocess.run(['netsh', 'wlan', 'show', 'profile', 
                                              f'"{profile}"', 'key=clear'], 
                                              capture_output=True, text=True, encoding='cp437')
                signal_match = re.search(r'Signal\s*:\s*(\d+)%', signal_result.stdout)
                signal = signal_match.group(1) if signal_match else "N/A"
                
                # Get security type
                security_match = re.search(r'Authenication\s*:\s*(.+)', signal_result.stdout)
                security = security_match.group(1).strip() if security_match else "Unknown"
                
                networks.append({
                    'SSID': profile,
                    'Signal': f"{signal}%",
                    'Security': security,
                    'Quality': self.signal_to_quality(signal)
                })
            return networks
        except Exception as e:
            print(f"Windows scan error: {e}")
            return []
    
    def scan_linux(self):
        """Linux WiFi scan using iwlist"""
        try:
            # Get wireless interface
            result = subprocess.run(['iwconfig'], capture_output=True, text=True)
            interface = re.search(r'(\w+)\s+IEEE', result.stdout)
            if not interface:
                return []
            interface = interface.group(1)
            
            # Scan
            result = subprocess.run(['sudo', 'iwlist', interface, 'scan'], 
                                  capture_output=True, text=True)
            
            networks = []
            ssid = None
            signal = None
            security = []
            
            for line in result.stdout.split('\n'):
                line = line.strip()
                
                # SSID
                ssid_match = re.search(r'ESSID:"([^"]+)"', line)
                if ssid_match:
                    if ssid:  # Save previous network
                        networks.append({
                            'SSID': ssid,
                            'Signal': f"{signal}dBm",
                            'Security': '/'.join(security) if security else 'Open',
                            'Quality': self.signal_to_quality(signal.replace('dBm', ''))
                        })
                    ssid = ssid_match.group(1)
                    signal = None
                    security = []
                
                # Signal strength
                signal_match = re.search(r'Signal level=(-?\d+) dBm', line)
                if signal_match:
                    signal = signal_match.group(1)
                
                # Security
                if 'WPA' in line or 'WPA2' in line or 'WPA3' in line:
                    security.append(line.split()[0])
                elif 'Encryption key:on' in line:
                    security.append('WEP')
            
            # Add last network
            if ssid:
                networks.append({
                    'SSID': ssid,
                    'Signal': f"{signal}dBm" if signal else "N/A",
                    'Security': '/'.join(security) if security else 'Open',
                    'Quality': self.signal_to_quality(signal.replace('dBm', '') if signal else '0')
                })
            
            return networks
        except Exception as e:
            print(f"Linux scan error: {e}")
            return []
    
    def scan_mac(self):
        """macOS WiFi scan using airport"""
        try:
            result = subprocess.run(['/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport', '-s'], 
                                  capture_output=True, text=True)
            
            networks = []
            lines = result.stdout.split('\n')[1:]  # Skip header
            for line in lines:
                if not line.strip() or line.startswith(' ' * 4):
                    continue
                parts = line.split()
                if len(parts) < 4:
                    continue
                
                ssid = parts[0]
                signal = parts[-3] + 'dBm'  # RSSI
                security = parts[-1] if len(parts) > 4 else 'Unknown'
                
                networks.append({
                    'SSID': ssid,
                    'Signal': signal,
                    'Security': security,
                    'Quality': self.signal_to_quality(signal.replace('dBm', ''))
                })
            return networks
        except Exception as e:
            print(f"macOS scan error: {e}")
            return []
    
    def signal_to_quality(self, signal):
        """Convert signal strength to quality bars"""
        try:
            sig = int(signal)
            if sig >= -30:
                return "█████"
            elif sig >= -50:
                return "████░"
            elif sig >= -60:
                return "███░░"
            elif sig >= -70:
                return "██░░░"
            else:
                return "█░░░░"
        except:
            return "░░░░░"
    
    def scan(self):
        """Scan for WiFi networks"""
        if self.system == "windows":
            return self.scan_windows()
        elif self.system == "linux":
            return self.scan_linux()
        elif self.system == "darwin":
            return self.scan_mac()
        else:
            print("Unsupported OS")
            return []
    
    def display_networks(self, networks):
        """Display networks in a formatted table"""
        if not networks:
            print("No networks found!")
            return
        
        print("\n" + "="*80)
        print(f"{'SSID':<25} {'Signal':<10} {'Quality':<6} {'Security':<20}")
        print("="*80)
        
        for net in sorted(networks, key=lambda x: x['Quality'], reverse=True):
            ssid = net['SSID'][:24]
            print(f"{ssid:<25} {net['Signal']:<10} {net['Quality']:<6} {net['Security'][:19]:<20}")
        
        print("="*80)
        print(f"Total: {len(networks)} networks found\n")

def main():
    scanner = WiFiScanner()
    
    print("🔍 WiFi Network Scanner")
    print("Press Ctrl+C to stop continuous scanning\n")
    
    try:
        while True:
            print(f"\n[{time.strftime('%H:%M:%S')}] Scanning...")
            networks = scanner.scan()
            scanner.display_networks(networks)
            time.sleep(5)  # Scan every 5 seconds
    except KeyboardInterrupt:
        print("\n👋 Scanner stopped!")

if __name__ == "__main__":
    main()
