from pyrosm import OSM
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import  plotly as py
import sys
from pyrosm import get_data
import matplotlib.pyplot as plt
from shapely.geometry import Polygon, Point
from fiona.crs import from_epsg
import os
from os import path
import csv
import pyproj
import geopandas
from shapely import ops
from functools import partial
import random
import getopt


def write_rows_to_csv(filename,rows,avg_area = 0):
    if not path.exists("results"):
        os.makedirs("results")
    filename = path.join("results",filename)
    file = open(filename,'w')
    writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    for row in rows:
        if row["area"] == 0:
            row["area"] = avg_area
        writer.writerow(row.values())
    file.close()

def random_points_within(poly, num_points,interiors):
  min_x, min_y, max_x, max_y = poly.bounds
  points = []
  while len(points) < num_points:
    random_point = Point([random.uniform(min_x, max_x), random.uniform(min_y, max_y)])
    flag = True
    for x in interiors:
        if random_point.within(x):
            flag = False
            break
    if (random_point.within(poly) and flag):
      points.append(random_point)

  return points

def calc_geom_area(poly):
  """
  Calcs area in square meters (polygon.area returns it in degrees, not so useful).
  """
  bounds = poly.bounds
  p = ops.transform(
  partial(
      pyproj.transform,
      pyproj.Proj('EPSG:4326'),
      pyproj.Proj(
          proj='aea',
          lat_1=bounds[1],
          lat_2=bounds[3])),
  poly)
  # Print the area in m^2
  return p.area

def merge(path):
    types = ["hospitals","houses","offices","parks","schools","supermarkets","place_of_worship"]
    frames = []
    for type in types:
        file = path+"/"+type+".csv"
        try:
            dataframe = pd.read_csv(file,names=["type","x","y","area"])
            frames.append(dataframe)
        except:
            print("file empty "+ file)
        # if dataframe.empty == True:
        #     print("file empty "+ file)
        # else:
        #     frames.append(dataframe)
    df = pd.concat(frames,ignore_index=True)
    df.to_csv(path+"/buildings.csv", index=False,header=None)

def extract_hospitals(osm):
    #what needs to be extracted
    custom_filter = {'amenity': ["doctors","clinic","clinic;hospital","hospital"]}
    # custom_filter = {'amenity': ["hospital"]}

    extracted_result = osm.get_pois(custom_filter=custom_filter)
    results = []
    areas = []
    print(str(len(extracted_result)) + " hospitals extracted")
    for x in range(len(extracted_result)):
        geo_gs = extracted_result.loc[[x], "geometry"] #geoseries object
        shap_gs = extracted_result.loc[x, "geometry"] # shapely object
        centroid = shap_gs.centroid
        if shap_gs.type == "Polygon":
            lon = centroid.x
            lat = centroid.y
            geo_gs.set_crs(epsg=4326)

            # 3857,3395,6933,{'proj':'cea'} : a few epsg strings to project to
            # most commonly used in web application is 3857 and 6933
            #
            # 3395 : used in very small scale mapping
            #source : https://epsg.io/3395
            #
            # 6933 and cea : not useful in our case: "The projection is appropriate for large-scale mapping of the areas near the equator such as Indonesia and parts of the Pacific Ocean. Its recommended use is for narrow areas extending along the standard lines. The projection is often misused for small-scale mapping."
            # source: https://pro.arcgis.com/en/pro-app/help/mapping/properties/cylindrical-equal-area.htm#:~:text=the%20central%20meridian.-,Usage,misused%20for%20small%2Dscale%20mapping.

            geo_gs = geo_gs.to_crs(epsg=3395)
            area = int((float(geo_gs.area)))
            # area = calc_geom_area(shap_gs) #uses albers equal area projection


            row = {"type":"hospital","lon":lon,"lat":lat,"area":area}
            areas.append(area)
            results.append(row)
        else:
            lon = centroid.x
            lat = centroid.y
            row = {"type": "hospital", "lon": lon, "lat": lat, "area": 0}
            results.append(row)
    write_rows_to_csv("hospitals.csv", results, int(sum(areas) / len(areas)))

def extract_offices(osm):
    # what needs to be extracted
    custom_filter = {'building': ["office"],"office":True}
    keys_to_keep = ["building","office"]
    extracted_result = osm.get_data_by_custom_criteria(custom_filter=custom_filter,osm_keys_to_keep=keys_to_keep,keep_nodes = True, keep_relations = True,keep_ways=True)
    results = []
    areas = []
    print(str(len(extracted_result)) + " offices extracted")
    for x in range(len(extracted_result)):
        geo_gs = extracted_result.loc[[x], "geometry"]  # geoseries object
        shap_gs = extracted_result.loc[x, "geometry"]  # shapely object
        centroid = shap_gs.centroid
        if shap_gs.type == "Polygon":
            lon = centroid.x
            lat = centroid.y
            geo_gs.set_crs(epsg=4326)

            # 3857,3395,6933,{'proj':'cea'} : a few epsg strings to project to
            # most commonly used in web application is 3857 and 6933
            #
            # 3395 : used in very small scale mapping
            # source : https://epsg.io/3395
            #
            # 6933 and cea : not useful in our case: "The projection is appropriate for large-scale mapping of the areas near the equator such as Indonesia and parts of the Pacific Ocean. Its recommended use is for narrow areas extending along the standard lines. The projection is often misused for small-scale mapping."
            # source: https://pro.arcgis.com/en/pro-app/help/mapping/properties/cylindrical-equal-area.htm#:~:text=the%20central%20meridian.-,Usage,misused%20for%20small%2Dscale%20mapping.

            # geo_gs = geo_gs.to_crs(epsg=3395)
            # area = int((float(geo_gs.area)))
            area = int(calc_geom_area(shap_gs)) #uses albers equal area projection

            row = {"type": "office", "lon": lon, "lat": lat, "area": area}
            areas.append(area)
            results.append(row)
        else:
            lon = centroid.x
            lat = centroid.y
            row = {"type": "office", "lon": lon, "lat": lat, "area": 0}
            results.append(row)
    write_rows_to_csv("offices.csv", results, int(sum(areas) / len(areas)))


def extract_leisure(osm):
    # what needs to be extracted
    # custom_filter = {'leisure': ["park","garden","nature_reserve","playground","track"]}
    custom_filter = {'leisure':True}
    keys_to_keep = ["leisure"]
    extracted_result = osm.get_data_by_custom_criteria(custom_filter=custom_filter,osm_keys_to_keep=keys_to_keep,keep_nodes = False, keep_relations = False,keep_ways=True)
    results = []
    areas = []
    print(str(len(extracted_result)) + " parks extracted")
    for x in range(len(extracted_result)):
        geo_gs = extracted_result.loc[[x], "geometry"]  # geoseries object
        shap_gs = extracted_result.loc[x, "geometry"]  # shapely object
        centroid = shap_gs.centroid
        leisure_type = extracted_result.loc[x,"leisure"]
        if leisure_type in ["park","garden","nature_reserve"]:
            leisure_type = "park"
        else:
            leisure_type = "leisure"
        if shap_gs.type == "Polygon":
            lon = centroid.x
            lat = centroid.y
            geo_gs.set_crs(epsg=4326)

            # 3857,3395,6933,{'proj':'cea'} : a few epsg strings to project to
            # most commonly used in web application is 3857 and 6933
            #
            # 3395 : used in very small scale mapping
            # source : https://epsg.io/3395
            #
            # 6933 and cea : not useful in our case: "The projection is appropriate for large-scale mapping of the areas near the equator such as Indonesia and parts of the Pacific Ocean. Its recommended use is for narrow areas extending along the standard lines. The projection is often misused for small-scale mapping."
            # source: https://pro.arcgis.com/en/pro-app/help/mapping/properties/cylindrical-equal-area.htm#:~:text=the%20central%20meridian.-,Usage,misused%20for%20small%2Dscale%20mapping.

            # geo_gs = geo_gs.to_crs(epsg=3395)
            # area = int((float(geo_gs.area)))
            area = int(calc_geom_area(shap_gs)) #uses albers equal area projection

            row = {"type": leisure_type, "lon": lon, "lat": lat, "area": area}
            areas.append(area)
            results.append(row)
        else:
            lon = centroid.x
            lat = centroid.y
            row = {"type": leisure_type, "lon": lon, "lat": lat, "area": 0}
            results.append(row)
    write_rows_to_csv("parks.csv", results, int(sum(areas) / len(areas)))

def extract_schools(osm):
    # what needs to be extracted
    custom_filter = {'amenity': ["school","university"], "building": ["school","university"]}
    keys_to_keep = ["building","amenity"]
    extracted_result = osm.get_data_by_custom_criteria(custom_filter=custom_filter,osm_keys_to_keep=keys_to_keep,keep_nodes = False, keep_relations = False,keep_ways=True)
    results = []
    areas = []
    print(str(len(extracted_result)) + " schools/universities extracted")
    for x in range(len(extracted_result)):
        geo_gs = extracted_result.loc[[x], "geometry"]  # geoseries object
        shap_gs = extracted_result.loc[x, "geometry"]  # shapely object
        centroid = shap_gs.centroid
        if shap_gs.type == "Polygon":
            lon = centroid.x
            lat = centroid.y
            geo_gs.set_crs(epsg=4326)

            # 3857,3395,6933,{'proj':'cea'} : a few epsg strings to project to
            # most commonly used in web application is 3857 and 6933
            #
            # 3395 : used in very small scale mapping
            # source : https://epsg.io/3395
            #
            # 6933 and cea : not useful in our case: "The projection is appropriate for large-scale mapping of the areas near the equator such as Indonesia and parts of the Pacific Ocean. Its recommended use is for narrow areas extending along the standard lines. The projection is often misused for small-scale mapping."
            # source: https://pro.arcgis.com/en/pro-app/help/mapping/properties/cylindrical-equal-area.htm#:~:text=the%20central%20meridian.-,Usage,misused%20for%20small%2Dscale%20mapping.

            # geo_gs = geo_gs.to_crs(epsg=3395)
            # area = int((float(geo_gs.area)))
            area = int(calc_geom_area(shap_gs)) #uses albers equal area projection

            row = {"type": "school", "lon": lon, "lat": lat, "area": area}
            areas.append(area)
            results.append(row)
        else:
            lon = centroid.x
            lat = centroid.y
            row = {"type": "school", "lon": lon, "lat": lat, "area": 0}
            results.append(row)
    write_rows_to_csv("schools.csv", results, int(sum(areas) / len(areas)))

def extract_supermarkets(osm):
    # what needs to be extracted
    #we need two filters, because of an odd issue, shops aren't extracted if they are included in first filter. Using two filters is justfied in
    # islamabad case since no shop is marked as a retail building or landuse, thus no same items are extracted by the two filters.
    #this might not be true in case of other cities
    custom_filter1 = {"landuse": ["retail"],"building": ["retail"]}
    custom_filter2 = {'shop': True}
    keep_nodes1 = False
    keep_nodes2 = False
    set1 = (custom_filter1,keep_nodes1)
    set2 = (custom_filter2,keep_nodes2)
    results = []
    areas = []
    for filter in [set1,set2]:
        extracted_result = osm.get_data_by_custom_criteria(custom_filter=filter[0],keep_nodes = filter[1], keep_relations = False,keep_ways=True)
        print(str(len(extracted_result)) + " shops/supermarkets extracted")
        for x in range(len(extracted_result)):
            try:
                t1 = extracted_result.loc[x, "shop"]
            except KeyError:
                t1 = None
            try:
                t2 = extracted_result.loc[x, "amenity"]
            except KeyError:
                t2 = None

            if t1 == "supermarket" or t2 == "supermarket":
                shop_type = "supermarket"
            else:
                shop_type = "shopping"
            geo_gs = extracted_result.loc[[x], "geometry"]  # geoseries object
            shap_gs = extracted_result.loc[x, "geometry"]  # shapely object
            centroid = shap_gs.centroid
            if shap_gs.type == "Polygon":
                lon = centroid.x
                lat = centroid.y
                geo_gs.set_crs(epsg=4326)

                # 3857,3395,6933,{'proj':'cea'} : a few epsg strings to project to
                # most commonly used in web application is 3857 and 6933
                #
                # 3395 : used in very small scale mapping
                # source : https://epsg.io/3395
                #
                # 6933 and cea : not useful in our case: "The projection is appropriate for large-scale mapping of the areas near the equator such as Indonesia and parts of the Pacific Ocean. Its recommended use is for narrow areas extending along the standard lines. The projection is often misused for small-scale mapping."
                # source: https://pro.arcgis.com/en/pro-app/help/mapping/properties/cylindrical-equal-area.htm#:~:text=the%20central%20meridian.-,Usage,misused%20for%20small%2Dscale%20mapping.

                # geo_gs = geo_gs.to_crs(epsg=3395)
                # area = int((float(geo_gs.area)))
                area = int(calc_geom_area(shap_gs)) #uses albers equal area projection

                row = {"type": shop_type, "lon": lon, "lat": lat, "area": area}
                areas.append(area)
                results.append(row)
            else:
                lon = centroid.x
                lat = centroid.y
                row = {"type": shop_type, "lon": lon, "lat": lat, "area": 0}
                results.append(row)
    write_rows_to_csv("supermarkets.csv", results, int(sum(areas) / len(areas)))


def extract_place_of_worship(osm):
    # what needs to be extracted
    custom_filter = {'amenity': ["place_of_worship"]}
    extracted_result = osm.get_data_by_custom_criteria(custom_filter=custom_filter,keep_nodes = True, keep_relations = True,keep_ways=True)
    results = []
    areas = []
    print(str(len(extracted_result)) + " places of worship extracted")
    for x in range(len(extracted_result)):
        geo_gs = extracted_result.loc[[x], "geometry"]  # geoseries object
        shap_gs = extracted_result.loc[x, "geometry"]  # shapely object
        centroid = shap_gs.centroid
        if shap_gs.type == "Polygon":
            lon = centroid.x
            lat = centroid.y
            geo_gs.set_crs(epsg=4326)

            # 3857,3395,6933,{'proj':'cea'} : a few epsg strings to project to
            # most commonly used in web application is 3857 and 6933
            #
            # 3395 : used in very small scale mapping
            # source : https://epsg.io/3395
            #
            # 6933 and cea : not useful in our case: "The projection is appropriate for large-scale mapping of the areas near the equator such as Indonesia and parts of the Pacific Ocean. Its recommended use is for narrow areas extending along the standard lines. The projection is often misused for small-scale mapping."
            # source: https://pro.arcgis.com/en/pro-app/help/mapping/properties/cylindrical-equal-area.htm#:~:text=the%20central%20meridian.-,Usage,misused%20for%20small%2Dscale%20mapping.

            # geo_gs = geo_gs.to_crs(epsg=3395)
            # area = int((float(geo_gs.area)))
            area = int(calc_geom_area(shap_gs)) #uses albers equal area projection

            row = {"type": "place_of_worship", "lon": lon, "lat": lat, "area": area}
            areas.append(area)
            results.append(row)
        else:
            lon = centroid.x
            lat = centroid.y
            row = {"type": "place_of_worship", "lon": lon, "lat": lat, "area": 0}
            results.append(row)
    write_rows_to_csv("place_of_worship.csv", results, int(sum(areas) / len(areas)))


def extract_houses(osm):
    FIVE_MARLA_HOUSE = 104.52  # in sq meter
    SEVEN_MARLA_HOUSE = 146.32  # in sq meter
    Islamabad_Population = 1129198  # from https://worldpopulationreview.com/world-cities/islamabad-population
    # Sector_Population = 50000
    Avg_HouseHold = 6.45 # https://tribune.com.pk/story/1491353/census-2017-family-size-shrinks
    Total_Num_of_Houses = int(Islamabad_Population / Avg_HouseHold)
    # Total_Num_of_Houses = 336182  # for islamabad, based on 2017 census


    poly_list = []
    results = []
    custom_filter = {'leisure': ["park"]}
    extracted_result = osm.get_data_by_custom_criteria(custom_filter=custom_filter,keep_nodes=False)
    custom_filter = {'landuse': ["residential"]}
    landuse = osm.get_landuse(custom_filter=custom_filter)
    for i in range(len(landuse)):
        land = landuse.loc[i, "geometry"]
        if land.geom_type == "Point":
            continue
        for j in range(len(extracted_result)):
            park = extracted_result.loc[j,"geometry"]
            if park.geom_type == "Point":
                continue
            elif park.within(land):
                land = land.difference(park)
        shap_gs = land
        # geo_gs = geopandas.GeoSeries(land)
        # geo_gs.set_crs(epsg=4326)
        # geo_gs.crs = "EPSG:4326"
        # 3857,3395,6933,{'proj':'cea'} : a few epsg strings to project to
        # most commonly used in web application is 3857 and 6933
        #
        # 3395 : used in very small scale mapping
        # source : https://epsg.io/3395
        #
        # 6933 and cea : not useful in our case: "The projection is appropriate for large-scale mapping of the areas near the equator such as Indonesia and parts of the Pacific Ocean. Its recommended use is for narrow areas extending along the standard lines. The projection is often misused for small-scale mapping."
        # source: https://pro.arcgis.com/en/pro-app/help/mapping/properties/cylindrical-equal-area.htm#:~:text=the%20central%20meridian.-,Usage,misused%20for%20small%2Dscale%20mapping.
        #
        # geo_gs = geo_gs.to_crs(epsg=3395)
        # area = int((float(geo_gs.area)))
        area = int(calc_geom_area(shap_gs)) #uses albers equal area projection
        interiors = list(shap_gs.interiors)
        temp_ply_list = []
        for x in interiors:
            ply = Polygon(x)
            temp_ply_list.append(ply)
            area -= calc_geom_area(ply)
        area = int(area)
        poly_list.append((shap_gs,shap_gs.centroid.x,shap_gs.centroid.y,area,temp_ply_list))

    total_Area = 0
    for p in poly_list:
        total_Area += p[3]
    for p in poly_list:
        areaPercent = p[3] / total_Area
        Num_of_Houses = int(Total_Num_of_Houses * areaPercent)
        # Num_of_Houses = p[3] / FIVE_MARLA_HOUSE
        houseArea = FIVE_MARLA_HOUSE
        points = random_points_within(p[0], Num_of_Houses, p[4])
        for h in points:
            row = {"type": "house", "lon": h.x, "lat": h.y, "area": houseArea}
            results.append(row)
    print(str(len(results)) + " houses generated")
    write_rows_to_csv("houses.csv", results,0)


def generate_loc_graph(path):
    try:
        df = pd.read_csv(path, header=None, delimiter=',')
    except Exception as e:
        print("Error: "+ str(e))
        return
    df.columns = ['type', 'x', 'y', 'area']
    groups = df.groupby('type').count()
    type = ['hospital', 'house', 'office', 'park', 'leisure', 'school', 'supermarket', 'shopping', "place_of_worship"]
    df['color'] = 0
    for index, row in df.iterrows():
        df['color'][index] = type.index(row['type'])
    fig = go.FigureWidget(px.scatter_mapbox(df, lat="y", lon="x",
                                            hover_name="type",
                                            color='color',
                                            color_continuous_scale=["darkgreen", "crimson", "orange", "lightgreen",
                                                                    "gold", "purple", "blue", "blue", "cyan"],
                                            zoom=8, height=800))

    fig.update_layout(mapbox_style="open-street-map")
    py.offline.plot(fig, filename='location_graph.html')
    # fig.show()


# Remove 1st argument from the
# list of command line arguments
argumentList = sys.argv[1:]
osm = OSM("../../OSM/islamabad.osm.pbf") # default
# Options
options = ""
# Long options
long_options = ["help","input=","merge","loc","houses","supermarkets","leisure","place_of_worship","all","offices","hospitals","schools"]

try:
    # Parsing argument
    arguments, values = getopt.getopt(argumentList,longopts=long_options,shortopts=options)

    # checking each argument
    for currentArgument, currentValue in arguments:
        if currentArgument in ("--help"):
            print("Parses input osm.pbf file, extracts variety of places and outputs a location graph")
            print("Inputs: ")
            print("--input <path to osm.pbf file to parse> : if you skip it the script will use a default osm file" )
            print("--leisure: to extract leisure places")
            print("--schools: to extract schools")
            print("--hospitals: to extract hospitals")
            print("--offices: to extract offices")
            print("--place_of_worship: to extract place of worship")
            print("--supermarkets: to extract supermarkets")
            print("--houses: to generate houses in residential areas")
            print("--merge: to merge indivdual results of supermarkets, leisure etc")
            print("--loc: to use the output of merge to generate location graph")
            print("--all: to do everything with default osm.pbf")
            break
        elif currentArgument in ("--all"):
            extract_leisure(osm)
            extract_schools(osm)
            extract_hospitals(osm)
            extract_offices(osm)
            extract_place_of_worship(osm)
            extract_supermarkets(osm)
            extract_houses(osm)
            merge("results")
            generate_loc_graph("results/buildings.csv")
            break
        elif currentArgument in ("--input"):
            osm = OSM(currentValue)
        elif currentArgument in ("--leisure"):
            extract_leisure(osm)
        elif currentArgument in ("--schools"):
            extract_schools(osm)
        elif currentArgument in ("--hospitals"):
            extract_hospitals(osm)
        elif currentArgument in ("--offices"):
            extract_offices(osm)
        elif currentArgument in ("--place_of_worship"):
            extract_place_of_worship(osm)
        elif currentArgument in ("--supermarkets"):
            extract_supermarkets(osm)
        elif currentArgument in ("--houses"):
            extract_houses(osm)
        elif currentArgument in ("--merge"):
            merge("results")
        elif currentArgument in ("--loc"):
            generate_loc_graph("results/buildings.csv")


except getopt.error as err:
    # output error, and return with an error code
    print(str(err))
