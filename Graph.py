import csv
from matplotlib import pyplot as plt

data_list = []
with open("graphs/plotData.csv", "r") as f:
    csv_reader = csv.reader(f)
    for row in csv_reader:
        data_list.append(row)

colors = {
    "Temperature = 0": "blue",
    "Temperature = 12": "green",
    "Temperature = 24": "yellow",
    "Temperature = 36": "purple",
    "Temperature = 48": "black",
    "Temperature = 60": "red",
}

plt.ylabel("Number of trees")
plt.xlabel("Iterations")
plt.title("Trees on fire per iteration")

for row in data_list:
    temperature = row.pop(0)
    Temperature2 = "Temperature = " + temperature.split(" = ")[1]
    color = colors[temperature]

    iterations_data = list(map(int, row))

    plt.plot(iterations_data, color=color, label=Temperature2)

plt.legend()
plt.savefig("graphs/Temperature.svg", format="svg")
plt.show()
