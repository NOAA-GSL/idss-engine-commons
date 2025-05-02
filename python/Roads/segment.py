from math import radians, degrees, sin, cos, asin, acos, sqrt
import json
import copy

segment_distance = 100


def great_circle_miles(lon1, lat1, lon2, lat2):
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    return 3958.756 * (acos(sin(lat1) * sin(lat2) + cos(lat1) * cos(lat2) * cos(lon1 - lon2)))


def subdividefeature(feature):
    # split one feature into multiple based on segment_distance
    totaldistance = 0
    newfeatures = []
    points = []
    featuress = []
    path = feature["geometry"]["coordinates"]
    for i in range(1, len(path)):
        lon1 = path[i - 1][0]
        lat1 = path[i - 1][1]
        lon2 = path[i][0]
        lat2 = path[i][1]
        totaldistance = totaldistance + great_circle_miles(lon1, lat1, lon2, lat2)
        points.append([lon1, lat1])
        # write points to array if we exceed segment_distance or if this is the last time through loop
        if totaldistance > segment_distance or i == len(path) - 1:
            totaldistance = 0
            # add last point to array
            points.append([lon2, lat2])
            # copy current feature
            feat = feature.copy()
            # overwrite old coordinates
            feat["geometry"]["coordinates"] = points.copy()
            # clear points for next segment
            points = []
            # add this feature to all features
            featuress.append(copy.deepcopy(feat))

    return featuress


def makenewfeature(data, outfile):
    features = []
    for feature in data["features"]:
        path = feature["geometry"]["coordinates"]
        newfeatures = subdividefeature(feature)
        features = features + newfeatures
    # Overwrite old features
    data["features"] = features

    # write to file
    with open(outfile, "w") as outfile:
        json.dump(data, outfile)


files = ["I-15.json", "I-25.json", "I-70.json", "I-80.json", "I-90.json", "I-94.json"]
# files = ["I-15.json"]
folder = "Compressed"

for file in files:
    path = folder + "/" + file
    outfile = folder + "/" + "segment_" + str(segment_distance) + "_" + file
    print(outfile)
    with open(path, "r") as f:
        makenewfeature(json.load(f), outfile)
