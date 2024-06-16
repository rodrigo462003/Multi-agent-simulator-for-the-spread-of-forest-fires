import csv
from matplotlib import pyplot as plt

data_list = []
with open("graphs/plotData.csv", "r") as f:
    csv_reader = csv.reader(f)
    for row in csv_reader:
        data_list.append(row)

colors = {
    "Humidity = 0": "blue",
    "Humidity = 25": "green",
    "Humidity = 50": "yellow",
    "Humidity = 75": "purple",
    "Humidity = 100": "red",
}
plt.ylabel("Number of trees")
plt.xlabel("Iterations")
plt.title("Trees burned per iteration")

for row in data_list:
    temperature = row.pop(0)
    Temperature2 = "Humidity = " + temperature.split(" = ")[1]
    color = colors[temperature]

    iterations_data = list(map(float, row))

    plt.plot(iterations_data, color=color, label=Temperature2)

plt.legend()
plt.savefig("graphs/RelativeHumidity.svg", format="svg")
plt.show()
