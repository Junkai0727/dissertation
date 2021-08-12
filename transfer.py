import pandas as pd


data = {}
average_data = {}
FILE = "GB_full.txt"

# 读取文件，获取邮编对应的经纬度
with open(FILE, 'r', encoding='utf-8') as file:
    for line in file:
        if line[-1] == "\n":
            line = line[:-1]
        line = line.split("\t")
        postcode = line[1].strip()
        # 得到经纬度
        latitude = float(line[-3])
        longitude = float(line[-2])
        data[postcode] = (latitude, longitude)

        # 维护一个邮编前缀为主键的字典，储存邮编前缀的平均经纬度
        prefix, suffix = postcode.split(" ")
        if prefix not in average_data:
            average_data[prefix] = [[], []]
        average_data[prefix][0].append(latitude)
        average_data[prefix][1].append(longitude)

keys = data.keys()

# 读取客户数据
dataframe = pd.read_csv("vaccination.csv", header=None, encoding="utf-8")
locations = dataframe.to_numpy().tolist()

count = []
results = []
for index in range(len(locations)):
    # 处理客户数据，数据清洗，得到干净的地址和邮编
    postcode = locations[index][2]
    postcode = postcode.strip()
    if "\xa0" in postcode:
        postcode = postcode.replace("\xa0", "")
    locations[index][2] = postcode
    locations[index][0] = locations[index][0].replace("\n", " ").replace("\xa0", "")

    # 如果数据库中没有邮编所对应的经纬度
    if postcode not in keys:
        # 如果数据库中有邮编前缀所对应的经纬度，用前缀的平均数作为邮编的经纬度
        prefix = postcode.split(" ")[0]
        if prefix in average_data:
            latitude = sum(average_data[prefix][0]) / len(average_data[prefix][0])
            longitude = sum(average_data[prefix][1]) / len(average_data[prefix][1])
            locations[index].append(latitude)
            locations[index].append(longitude)
            print(f"cannot find {postcode}, use {prefix} instead")
            continue
        # 如果数据库中没有邮编前缀所对应的经纬度，写入None
        count.append(postcode)
        print(f"cannot find {postcode}")
        locations[index].append(None)
        locations[index].append(None)
        continue

    # 如果数据库中有邮编所对应的经纬度
    latitude, longitude = data[postcode]
    locations[index].append(latitude)
    locations[index].append(longitude)

with open("vaccination_output.txt", "w", encoding="utf-8") as file:
    for line in locations:
        # 将地址，邮编，latitude，longitude 写入文件
        file.write(line[0] + "\t" + line[2] + "\t" + str(line[3]) + "\t" + str(line[4]) + "\n")

print()
print(f"There is {len(count)} postcode cannot find. They are {count}")
print("Finish.")
