import csv

rows = []
number = ""
with open("graphs/plotDataOnFire.csv", "r") as f:
    csv_reader = csv.reader(f)
    for row in csv_reader:
        number = row.pop(0)
        rows.append(row)

result = [
    (int(x) + int(y) + int(z) + int(w) + int(v)) / 5 for x, y, z, w, v in zip(*rows)
]
result.insert(0, number)
with open("graphs/plotData.csv", "a") as f2:
    for i in result:
        f2.write(str(i) + ",")
    f2.write("\n")

rows = []
number = ""
with open("graphs/plotDataDead.csv", "r") as f:
    csv_reader = csv.reader(f)
    for row in csv_reader:
        number = row.pop(0)
        rows.append(row)

result = [
    (int(x) + int(y) + int(z) + int(w) + int(v)) / 5 for x, y, z, w, v in zip(*rows)
]
result.insert(0, number)
with open("graphs/plotData2.csv", "a") as f2:
    for i in result:
        f2.write(str(i) + ",")
    f2.write("\n")
