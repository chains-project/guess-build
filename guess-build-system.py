#!/usr/bin/env python3

"""
Build System Detection Tool

This script analyzes a directory to detect common build systems and package managers
by looking for characteristic files and patterns.

Supported build systems:
- Maven (Java)
- Gradle (Java/Kotlin)
- npm/Yarn (JavaScript/Node.js)
- Python (pip/Poetry)
- CMake/Make (C/C++)
- Cargo (Rust)
- Composer (PHP)
- Bazel
- Ant (Java)
- sbt (Scala)
- Go Modules
- Lazarus (Free Pascal)
- SCons

Usage:
    ./guess-build-system.py         # Check current directory
    ./guess-build-system.py --json  # Output results in JSON format

Examples:
    $ cd /path/to/project
    $ guess-build-system.py
    
    Detected build systems:
    🔨 npm
      Found files:
       - package.json
       - package-lock.json
"""

import os
import json
from pathlib import Path
import argparse
import re  # Add re import

class BuildSystemDetector:
    def __init__(self):
        # Dictionary of build systems and their typical files/indicators using regex patterns
        self.build_systems = {
            'Maven': [r'^pom\.xml$'],
            'Gradle': [r'^build\.gradle(\.kts)?$', r'^settings\.gradle$', r'^gradlew$'],
            'npm': [r'^package(-lock)?\.json$', r'^npm-shrinkwrap\.json$'],
            'Yarn': [r'^yarn\.lock$'],
            'Python/pip': [r'^requirements.*\.txt$', r'^setup\.py$', r'^pyproject\.toml$'],
            'Poetry': [r'^poetry\.lock$'],
            'CMake': [r'^CMakeLists\.txt$'],
            'Make': [r'^[Mm]akefile$'],
            'Cargo (Rust)': [r'^Cargo\.(toml|lock)$'],
            'Composer (PHP)': [r'^composer\.(json|lock)$'],
            'Bazel': [r'^WORKSPACE$', r'^BUILD(\.bazel)?$'],
            'Ant': [r'^build\.xml$'],
            'sbt (Scala)': [r'^build\.sbt$'],
            'Go Modules': [r'^go\.(mod|sum)$'],
            'Lazarus': [r'^.*\.(lpi|lpr|lpk)$'],
            'SCons': [r'^SConstruct$', r'^SConscript$'] 
        }

    def detect_build_system(self, directory='.'):
        """
        Detect build systems in the given directory.
        Returns a list of detected build systems.
        """
        detected_systems = []
        dir_path = Path(directory)
        
        # Get files from current directory and immediate subdirectories
        all_files = []
        # Add files from current directory
        all_files.extend(f for f in dir_path.iterdir() if f.is_file())
        # Add files from immediate subdirectories
        for subdir in dir_path.iterdir():
            if subdir.is_dir():
                all_files.extend(f for f in subdir.iterdir() if f.is_file())
            
        # Check for each build system using regex patterns
        for system, patterns in self.build_systems.items():
            for pattern in patterns:
                matches = [
                    file for file in all_files 
                    if re.match(pattern, file.name, re.IGNORECASE)
                ]
                if matches:
                    detected_systems.append({
                        'system': system,
                        'found_files': matches
                    })
                    break

        return detected_systems

    def detect_package_type(self, directory='.'):
        """
        Try to detect more specific information about the project type
        based on package files.
        """
        package_info = {}
        
        # Check package.json for npm/Node.js projects
        package_json_path = Path(directory) / 'package.json'
        if package_json_path.exists():
            try:
                with open(package_json_path, 'r') as f:
                    data = json.load(f)
                    package_info['name'] = data.get('name', 'Unknown')
                    package_info['version'] = data.get('version', 'Unknown')
                    package_info['dependencies'] = list(data.get('dependencies', {}).keys())
            except json.JSONDecodeError:
                pass

        return package_info

def main():
    # Add argument parser
    parser = argparse.ArgumentParser(description='Detect build systems in current directory')
    parser.add_argument('--json', '-j', action='store_true', 
                      help='Output results in JSON format')
    args = parser.parse_args()
    
    detector = BuildSystemDetector()
    detected = detector.detect_build_system()
    
    if not detected:
        if args.json:
            print(json.dumps({"systems": [], "package_info": None}))
        else:
            print("No known build system detected.")
        return
    
    package_info = detector.detect_package_type()
    
    if args.json:
        # Format JSON output
        result = {
            "systems": [
                {
                    "name": system["system"],
                    "files": [str(f) for f in system["found_files"]]
                } for system in detected
            ],
            "package_info": package_info
        }
        print(json.dumps(result, indent=2))
    else:
        print("Detected build systems:")
        for system in detected:
            print(f"\n🔨 {system['system']}")
            print("  Found files:")
            for file in system['found_files']:
                print(f"   - {file}")
        
        # Get additional package information if available
        package_info = detector.detect_package_type()
        if package_info:
            print("\nPackage information:")
            for key, value in package_info.items():
                if isinstance(value, list):
                    print(f"\n{key}:")
                    for item in value[:5]:  # Show first 5 dependencies
                        print(f"  - {item}")
                    if len(value) > 5:
                        print(f"  ... and {len(value)-5} more")
                else:
                    print(f"{key}: {value}")

if __name__ == "__main__":
    main()

