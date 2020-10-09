from src.parse_osm import *
results = []


def extract_places(query):
    for c1 in root:
        if c1.tag == "way":
            for c2 in c1:
                if get_tag(c2, "amenity") == query:
                    p = get_polygon_from_way(c1, node_list)
                    if p:
                        results.append((query, p.centroid.x, p.centroid.y, int(calc_geom_area(p))))
        elif c1.tag == "node":
            for c2 in c1:
                if get_tag(c2, "amenity") == query:
                    results.append((query, c1.attrib["lon"], c1.attrib["lat"], 200))


if __name__ == "__main__":
    tree = ET.parse(sys.argv[1])
    root = tree.getroot()

    leisure_types = {}
    node_list = build_node_list(root)

    extract_places(sys.argv[2])
    print(results)
    if len(results) > 0:
        out = sys.argv[2] + '.csv'
        with open(out, "w") as outFile:
            for place in results:
                outFile.write(
                    "{},{},{},{}".format(place[0], place[1], place[2], place[3]))
                outFile.write("\n")
    else:
        print("No results found")
