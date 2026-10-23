import openeo

connection = openeo.connect("openeofed.dataspace.copernicus.eu")

with open('data/credentials.txt', 'r', encoding='utf-8') as file:
    for line in file:
        check = line.split(": ")
        if check[0] == "OAuth Client ID":
            ACCESS_KEY = check[1][:-1]
        elif check[0] == "OAuth Client secret":
            SECRET_KEY = check[1][:-1]

connection.authenticate_oidc_client_credentials(
    client_id=ACCESS_KEY,
    client_secret=SECRET_KEY
)

# collection_list = connection.list_collection_ids()
cube = connection.load_collection(
    "SENTINEL2_L2A",
    spatial_extent={"west": 1.322994, "south": 43.569322, "east": 1.483412, "north": 43.632845},
    temporal_extent=["2026-07-01", "2026-07-15"],
    bands=["B04", "B03", "B02"],
    max_cloud_cover=30
)

# Rescale 0–3000 → 0–255 (on clippe le haut : les réflectances dépassent rarement 30 %)
cube = cube.linear_scale_range(input_min=0, input_max=2000, output_min=0, output_max=255)

job = cube.execute_batch(out_format="PNG")
results = job.get_results()

# Try un split par underscore plutôt
for link in results.get_metadata()["links"]:
    if 'title' in link:
        if link["title"].startswith("Derived from S2"):
            dl_date = link["href"][11:19]

# Check si la date est correcte lorsqu'il y a plusieurs assets
results.get_assets()[0].download("data/downloads/" + dl_date + ".png")