import topojson
import sqlite3
import geojson

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

for row in result:
    company = row[0]
    cur = db.cursor()
    cur.execute("SELECT ATTACHMENT_TYPE, LONGITUDE, LATITUDE, ATTACHMENTNUMBER FROM [All_Active_and_Inactive_Joint_Use_Assets_2021-05-15] WHERE renter_company = ? AND LONGITUDE IS NOT NULL", (company,))
    
    features = []
    for t, lng, lat, num in cur:

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
    topojson.Topology(geojson.FeatureCollection(features)).to_json(fp=f"{company}.topojson")
