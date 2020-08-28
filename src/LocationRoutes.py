from pyroutelib3 import Router # Import the router
import osmnx as ox
import networkx as nx

# G = ox.graph_from_place('Piedmont, California, USA', network_type='drive')

G = ox.graph_from_xml("../OSM/i10.osm",bidirectional=True)
gdf_edges = ox.graph_to_gdfs(G, nodes=False)
# fig, ax = ox.plot_graph(G)
G = ox.add_edge_speeds(G)
# G = ox.add_edge_travel_times(G)
edges = ox.graph_to_gdfs(G, nodes=False)
orig = ox.get_nearest_node(G, (33.65077,73.02528))
dest = ox.get_nearest_node(G, (33.64801,73.04175))
route = nx.shortest_path(G, orig, dest, weight='travel_time')
length = nx.shortest_path_length(G, source=orig, target=dest, weight='length')
print(length)
print(route)
fig, ax = ox.plot_graph_route(G, route, node_size=0)
router = Router("car","../OSM/i10.osm") # Initialise it
print(router.nodeLatLon(route[0]))



# start = router.findNode(33.64725,73.03760) # Find start and end nodes
# end = router.findNode(33.6680,73.0753)
# status, route = router.doRoute(start, end) # Find the route - a list of OSM nodes
# if status == 'success':
#     routeLatLons = list(map(router.nodeLatLon, route)) # Get actual route coordinates
#     print(routeLatLons)
