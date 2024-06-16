import mesa
from mesa import Model, Agent
from mesa.visualization.UserParam import Slider, Choice
from mesa.visualization.modules import ChartModule
import matplotlib.pyplot as plt
import random
import nest_asyncio
import math
import atexit
import os

nest_asyncio.apply()

K_DISTANCIA = 0.05
K_VENTO = 0.150
K_TEMPERATURA = 0.35
K_HUMIDADE = 0.35
K_TIPO_DE_ARVORE = 0.1

arvoresArdidas = [1]
arvoresQueimadas = [1]
arvoresProbabilidade = {"Pine Tree": 0.3, "Eucalyptus": 0.5, "Oak Tree": 0.2}

windDirection = {
    "W": math.pi,
    "NW": 3 * math.pi / 4,
    "N": math.pi / 2,
    "NE": math.pi / 4,
    "E": 0,
    "SE": -math.pi / 4,
    "S": -math.pi / 2,
    "SW": -3 * math.pi / 4,
}


def exit_handler():
    # plt.ylabel("Number of trees")
    # plt.xlabel("Iterations")
    # plt.title("Trees on fire and trees burned per iteration")
    # plt.plot(arvoresArdidas, color="red", label="Trees on fire")
    # plt.plot(arvoresQueimadas, color="black", label="Trees burned")
    with open("graphs/plotDataOnFire.csv", "a") as f:
        f.write("Humidity = 100," + str(arvoresArdidas)[1:-1] + "\n")
    with open("graphs/plotDataDead.csv", "a") as f2:
        f2.write("Humidity = 100," + str(arvoresQueimadas)[1:-1] + "\n")
    # plt.legend()
    # plt.savefig("graphs/ExtremeMin.svg", format="svg")
    os._exit()


atexit.register(exit_handler)


class Tree(Agent):
    def __init__(self, id, model):
        super().__init__(id, model)

        self.id = id
        self.condition = "Fine"
        self.stepsOnFire = 0
        # self.new_condition = None

    def cardinal_direction(self, point1, point2):
        dx = point2[0] - point1[0]
        dy = point2[1] - point1[1]

        angle = math.atan2(dy, dx)
        return angle

    def step(self):
        if self.condition == "OnFire":
            self.stepsOnFire += 1
            if self.stepsOnFire >= 12:
                self.model.newBurned += 1
                self.condition = "Burned"
                return
        if self.condition != "Fine":
            return
        grid = self.model.grid
        neighbors = grid.get_neighbors(self.pos, moore=True, radius=2)
        for neighbor in neighbors:
            if neighbor.condition != "OnFire":
                continue
            distance = (
                (self.pos[0] - neighbor.pos[0]) ** 2
                + (self.pos[1] - neighbor.pos[1]) ** 2
            ) ** 0.5
            pDistancia = 1 - ((distance - 1) / (18**0.5 - 1))
            angle = -math.cos(
                self.cardinal_direction(self.pos, neighbor.pos)
                - windDirection[self.model.direcaoDoVento]
            )

            pVento = (self.model.velocidade * angle + 200) / 400
            # print(pVento)
            pTipoArvore = arvoresProbabilidade[self.model.TipoDeVegetacao]
            """
            print(
                "pTipoArvore:",
                pTipoArvore,
                "\n",
                "pDistancia:",
                pDistancia,
                "\n",
                "angle:",
                angle,
                "\n",
                "pVento:",
                pVento,
                "\n",
                "self.model.pTemperatura:",
                self.model.pTemperatura,
                "\n",
                "self.model.pHumidade:",
                self.model.pHumidade,
            )
            """
            probability = (
                K_DISTANCIA * pDistancia
                + K_VENTO * pVento
                + K_TEMPERATURA * self.model.pTemperatura
                + K_HUMIDADE * self.model.pHumidade
                + K_TIPO_DE_ARVORE * pTipoArvore
            ) * 0.05612
            # print("probability", probability / 0.05612, "\n")
            if random.random() < probability:
                self.model.setFire.append(self)
                break


class Fire(Model):
    def __init__(
        self,
        NArvores,
        Humidade,
        VelocidadeVento,
        DirecaoDoVento,
        TipoDeVegetacao,
        Temperatura,
    ):
        super().__init__()
        self.num_trees = NArvores
        self.humidade = Humidade
        self.velocidade = VelocidadeVento
        self.direcaoDoVento = DirecaoDoVento
        self.TipoDeVegetacao = TipoDeVegetacao
        self.Temperatura = Temperatura
        self.pTemperatura = self.Temperatura / 60
        self.pHumidade = 1 - self.humidade / 100
        self.numIterations = 0
        self.maxIterations = 500
        self.newBurned = 0
        self.setFire = []
        global arvoresArdidas
        arvoresArdidas = [1]
        global arvoresQueimadas
        arvoresQueimadas = [1]
        self.time = 0
        self.schedule = mesa.time.RandomActivation(self)
        self.grid = mesa.space.SingleGrid(100, 100, False)
        all_coordinates = [
            (x, y) for x in range(self.grid.width) for y in range(self.grid.height)
        ]

        random.shuffle(all_coordinates)

        for i in range(self.num_trees):
            a = Tree(i, self)
            self.schedule.add(a)
            x, y = all_coordinates[i]
            self.grid.place_agent(a, (x, y))

        self.startFire()

    def startFire(self):
        # começar cenarios sempre na mesma posição em testes...
        random_agent = random.choice(self.schedule.agents)
        random_agent.condition = "OnFire"

    def step(self):
        self.numIterations += 1
        if self.numIterations > self.maxIterations:
            exit_handler()
        self.schedule.step()
        treesBurned = arvoresArdidas[-1]
        for agent in self.setFire:
            agent.condition = "OnFire"
            treesBurned += 1
        arvoresQueimadas.append(arvoresQueimadas[-1] + self.newBurned)
        treesBurned = treesBurned - self.newBurned
        self.setFire = []
        self.newBurned = 0
        arvoresArdidas.append(treesBurned)


def agent_portrayal(agent):
    Shape = "circle"
    Color = "green"
    if agent.condition == "Burned":
        Color = "black"
    elif agent.condition == "OnFire":
        Color = "red"
    Filled = "true"
    Layer = 0
    r = 0.5
    return {"Shape": Shape, "Color": Color, "Filled": Filled, "Layer": Layer, "r": r}


grid = mesa.visualization.CanvasGrid(agent_portrayal, 100, 100, 500, 500)

chart = ChartModule([{"Label": "TreesOnFire", "Color": "red"}])
server = mesa.visualization.ModularServer(
    Fire,
    [grid],
    "Forest Fire",
    {
        "NArvores": Slider("Number of trees", 5000, 1, 10000),
        "Humidade": Slider("Relative Humidity(%)", 65, 0, 100),
        "VelocidadeVento": Slider("Wind Speed(km/h)", 26, 0, 200),
        "DirecaoDoVento": Choice(
            "Wind Direction",
            value="N",
            choices=["N", "NE", "E", "SE", "S", "SW", "W", "NW"],
        ),
        "TipoDeVegetacao": Choice(
            "Vegetation Type",
            value="Pine Tree",
            choices=["Pine Tree", "Eucalyptus", "Oak Tree"],
        ),
        "Temperatura": Slider("Temperature(°C)", 14, 0, 60),
    },
)
server.port = 8521
server.launch()
