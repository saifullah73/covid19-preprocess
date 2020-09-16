from pyrosm import OSM
from pyrosm import get_data
import matplotlib.pyplot as plt
# fp = get_data("test_pbf")
# osm = OSM(fp)
# buildings = osm.get_buildings()
# buildings.plot()
# # print(buildings)
# plt.show()





# Initialize the OSM parser object
osm = OSM("../OSM/i10.osm.pbf")
osm2 = OSM("../OSM/islamabad.osm.pbf")

#landuse
# landuse = osm.get_landuse()
# landuse.plot(column='landuse', legend=True, figsize=(10,6))
# plt.show()

#network
# network = osm.get_network(network_type="driving")
# print(network)
# network.plot()
# plt.show()

#builidngs
# buildings = osm.get_buildings()
# print(buildings)
# buildings.plot()
# plt.show()

#POI
# custom_filter = {'amenity': True, "shop": True}
# pois = osm2.get_pois(custom_filter=custom_filter)
# # pois = osm.get_pois()
#
# # Gather info about POI type (combines the tag info from "amenity" and "shop")
# print(pois.head())
# pois["poi_type"] = pois["amenity"]
# pois["poi_type"] = pois["poi_type"].fillna(pois["shop"])
# # pois["poi_type"] = pois["poi_type"].fillna(pois["tourism"])
#
# # Plot
# ax = pois.plot(column='poi_type', markersize=3, figsize=(12,12), legend=True, legend_kwds=dict(loc='upper left', ncol=3, bbox_to_anchor=(1, 1)))
# plt.show()


#natural
# natural = osm2.get_natural()
# natural.plot(column='natural', legend=True, figsize=(10,6))
# plt.show()

#boundaries
# boundaries = osm.get_boundaries()
# print(boundaries)
# boundaries.plot(facecolor="none", edgecolor="blue")
# plt.show()








