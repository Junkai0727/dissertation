import pandas as pd


data = {}
average_data = {}
FILE = "GB_full.txt"

# Read the file and get the latitude and longitude corresponding to the zip code
with open(FILE, 'r', encoding='utf-8') as file:
    for line in file:
        if line[-1] == "\n":
            line = line[:-1]
        line = line.split("\t")
        postcode = line[1].strip()
        # Get latitude and longitude
        latitude = float(line[-3])
        longitude = float(line[-2])
        data[postcode] = (latitude, longitude)

        # Maintain a dictionary with zip code prefix as the primary key, storing the average latitude and longitude of zip code prefixes
        prefix, suffix = postcode.split(" ")
        if prefix not in average_data:
            average_data[prefix] = [[], []]
        average_data[prefix][0].append(latitude)
        average_data[prefix][1].append(longitude)

keys = data.keys()

# Read data
dataframe = pd.read_csv("vaccination.csv", header=None, encoding="utf-8")
locations = dataframe.to_numpy().tolist()

count = []
results = []
for index in range(len(locations)):
    # Process data, data cleaning, get clean addresses and zip codes
    postcode = locations[index][2]
    postcode = postcode.strip()
    if "\xa0" in postcode:
        postcode = postcode.replace("\xa0", "")
    locations[index][2] = postcode
    locations[index][0] = locations[index][0].replace("\n", " ").replace("\xa0", "")

    # If the latitude and longitude corresponding to the zip code are not available in the database
    if postcode not in keys:
        # If the database has the latitude and longitude corresponding to the prefix of the zip code, use the average of the prefix as the latitude and longitude of the zip code
        prefix = postcode.split(" ")[0]
        if prefix in average_data:
            latitude = sum(average_data[prefix][0]) / len(average_data[prefix][0])
            longitude = sum(average_data[prefix][1]) / len(average_data[prefix][1])
            locations[index].append(latitude)
            locations[index].append(longitude)
            print(f"cannot find {postcode}, use {prefix} instead")
            continue
        # If there is no latitude and longitude in the database for the zip code prefix, write None
        count.append(postcode)
        print(f"cannot find {postcode}")
        locations[index].append(None)
        locations[index].append(None)
        continue

    # If the database has the latitude and longitude corresponding to the zip code
    latitude, longitude = data[postcode]
    locations[index].append(latitude)
    locations[index].append(longitude)

with open("vaccination_output.txt", "w", encoding="utf-8") as file:
    for line in locations:
        # Write the address, zip code, latitude, and longitude to the file
        file.write(line[0] + "\t" + line[2] + "\t" + str(line[3]) + "\t" + str(line[4]) + "\n")

print()
print(f"There is {len(count)} postcode cannot find. They are {count}")
print("Finish.")
