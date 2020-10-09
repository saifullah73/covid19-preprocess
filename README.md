# covid19-preprocess
Repo for essential preprocessing scripts for the Covid19 simulations. Additional documentation is available here: https://facs.readthedocs.io/en/latest/preparation.html

## Obtaining an OSM file.
OSM files are obtained from either Openstreetmaps.org, or using the OSRM tool.

## Extracting locations
You can do this using:
`python3 extract_<location_type>.py <osm_file> > <out_dir>/<location_type>.csv`

## Creating a buildings.csv for FACS
To create a buildings.csv for FACS, simply concatenate all the previously extracted locations into one CSV file.

## How to use new-parser/osm_parser.py
Parses input osm.pbf file, extracts variety of places and outputs a location graph. 
The script accepts multiple parameters as input  
1) --input <path to osm.pbf file to parse> : if you skip it the script will use a default osm file  
2) --leisure: to extract leisure places  
3) --schools: to extract schools  
4) --hospitals: to extract hospitals  
5) --offices: to extract offices  
6) --place_of_worship: to extract place of worship  
7) --supermarkets: to extract supermarkets  
8) --houses: to generate houses in residential areas  
9) --merge: to merge individual results of supermarkets, leisure etc  
10) --loc: to use the output of merge to generate location graph  
11) --all: to do everything with default osm.pbf  
`python3 osm_parser.py --input ../../OSM/islamabad.osm.pbf --leisure --schools --merge --loc `