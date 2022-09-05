import topojson
import sqlite3
import geojson
import math
from rtree import index

db = sqlite3.connect("file:/home/tannewt/repos/scl-attachments/attachments.db?mode=ro", uri=True)
result = db.execute("SELECT DISTINCT renter_company FROM [All_Active_and_Inactive_Joint_Use_Assets_2021-05-15]")

SYMBOLS = {
    "CABLE": "circle",
    "PWRSUPPLY10A": "charging-station",
    "PWRSUPPLY20A": "charging-station",
    "PWRSUPPLY30A": "charging-station",
    "CABINET": "square",
    "CAMERA": "attraction",
    "SMALL CELL": "mobile-phone",
    "CELL ANTENNA": "mobile-phone",
    "AMR": "bank",
    "AMR CONTROL STATION": "bank",
    "AMI ROUTER": "bank",
    "AMI COLLECTOR": "bank",
    "ANTENNA": "communications-tower",
    "STRANDANTENNA": "communications-tower",
    "WIRELESS ACCESS PT": "communications-tower",
    "WIFI": "communications-tower",
    "SIGN": "art-gallery",
    "MISC": "triangle"
}

MAX_DISTANCE = 0.002

for row in result:
# for row in (("BILL PIERRE FORD",),):
    company = row[0]
    print(company)
    cur = db.cursor()
    cur.execute("SELECT ATTACHMENT_TYPE, LONGITUDE, LATITUDE, ATTACHMENTNUMBER FROM [All_Active_and_Inactive_Joint_Use_Assets_2021-05-15] WHERE renter_company = ? AND LONGITUDE IS NOT NULL", (company,))
    
    features = []
    point_index = index.Index(interleaved=False)
    cable_points = {}
    for t, lng, lat, num in cur:
        if not lng or not lat:
            continue

        if t == "CABLE":
            point_index.insert(num, (lng, lng, lat, lat))
            cable_points[num] = (lng, lat)
            continue

        symbol = ""
        if t not in SYMBOLS:
            print(t)
        else:
            symbol = SYMBOLS[t]
        #print(lng, lat)

        feature = geojson.Feature(
            geometry=geojson.Point((lng, lat)),
            properties= {
                "marker-symbol": symbol,
                "marker-size": "small",
                "title": str(num),
                "description": t
            }
        )
        features.append(feature)

    while cable_points:
        starting_point = list(cable_points.keys())[0]
        pole_ids = [starting_point]

        lng, lat = cable_points[starting_point]
        del cable_points[starting_point]
        nearest = point_index.nearest((lng, lng, lat, lat), num_results=6)
        polyline = [(lng, lat)]
        last_angle = None
        for i in nearest:
            if i not in cable_points:
                continue
            nlng, nlat = cable_points[i]
            pole_ids.append(i)
            del cable_points[i]
            if lng - nlng == 0:
                dist = abs(lat - nlat)
                angle = 90
            else:
                dist = math.hypot(lng - nlng, lat - nlat)
                angle = math.degrees(math.atan((lat - nlat) / (lng - nlng)))
            # print(i, nlng, nlat, dist, angle)
            if dist == 0:
                continue
            if dist > MAX_DISTANCE:
                break
            if last_angle is None:
                polyline.append((nlng, nlat))
                last_angle = angle
            elif not math.isclose(last_angle, angle, abs_tol=15):
                polyline.insert(0, (nlng, nlat))
                break

        if len(polyline) == 1:
            pole_ids = [str(p) for p in pole_ids]
            feature = geojson.Feature(
                geometry=geojson.Point(polyline[0]),
                properties= {
                    "marker-symbol": "c",
                    "marker-size": "small",
                    "title": pole_ids[0],
                    "description": ", ".join(pole_ids)
                }
            )
            features.append(feature)
            continue

            # insert a point
        
        if len(polyline) == 3:
            # insert from the beginning
            last_point = polyline[1]
            next_point = polyline[0]
            while next_point:
                lng, lat = next_point
                nearest = point_index.nearest((lng, lng, lat, lat), num_results=6)
                next_point = None
                for i in nearest:
                    if i not in cable_points:
                        continue
                    nlng, nlat = cable_points[i]
                    if lng - nlng == 0 and lat - nlat == 0:
                        pole_ids.append(i)
                        del cable_points[i]
                        continue
                    dist = math.hypot(lng - nlng, lat - nlat)
                    # print("n", nlng, nlat, dist)
                    if dist > MAX_DISTANCE:
                        break
                    polyline.insert(0, (nlng, nlat))
                    pole_ids.append(i)
                    del cable_points[i]
                    next_point = (nlng, nlat)
                #print()
            # print(polyline)

        last_point = polyline[-2]
        next_point = polyline[-1]
        while next_point:
            lng, lat = next_point
            nearest = point_index.nearest((lng, lng, lat, lat), num_results=6)
            next_point = None
            for i in nearest:
                if i not in cable_points:
                    continue
                nlng, nlat = cable_points[i]
                if lng - nlng == 0 and lat - nlat == 0:
                    pole_ids.append(i)
                    del cable_points[i]
                    continue
                dist = math.hypot(lng - nlng, lat - nlat)
                #print("n", nlng, nlat, dist)
                if dist > MAX_DISTANCE:
                    break
                polyline.append((nlng, nlat))
                pole_ids.append(i)
                del cable_points[i]
                next_point = (nlng, nlat)
            # print()
        # print(polyline)

        pole_ids = [str(p) for p in pole_ids]
        # print(polyline)
        feature = geojson.Feature(
            geometry=geojson.LineString(polyline),
            properties= {
                "title": pole_ids[0],
                "description": ", ".join(pole_ids)
            }
        )
        features.append(feature)
    topojson.Topology(geojson.FeatureCollection(features)).to_json(fp=f"{company}.topojson")
