class Panel():

    width: int = 0
    height: int = 0
    side: str = "LEFT"
    paneles_vertical = 1
    paneles_horizontal = 1
    incrementar = False
    total_leds = 0
    total_leds_panel = 0
    altura_total = 0
    matriz = []

    def __init__(self,width, height, side = "LEFT", paneles_vertical = 1, paneles_horizontal = 1):
        self.width = width
        self.height = height
        self.side= side
        self.paneles_vertical = paneles_vertical
        self.paneles_horizontal = paneles_horizontal
        if self.side == "LEFT":
            self.incrementar = False
        else:
            self.incrementar= True

        self.total_leds = (width * paneles_horizontal) * (height * paneles_vertical)
        self.total_leds_panel = (width ) * (height )
        self.altura_total = height * paneles_vertical


    def calculateMatrix(self):
        self.matriz = []
        for i in range(self.altura_total, 0, -1):
            rangeMatrixLine = []
            linetemp = []

            # Calculate Max and min led
            maxled = (i * self.width)
            minled = (maxled - int(self.width))

            # For calculate go and return
            if self.incrementar == False:
                rangeMatrixLine.extend(range(maxled - 1, minled - 1, -1))
                self.incrementar = True
            else:
                rangeMatrixLine.extend(range(minled, maxled, 1))
                self.incrementar = False;

            #print("Range line {0}".format(i))
            #print(rangeMatrixLine)

            for p in range(self.paneles_horizontal):
                valorSuma = (p) * self.total_leds_panel
                line = list(map(lambda x: x + valorSuma, rangeMatrixLine))
                #print("line {0} panel {1}".format(i, p))
                #print(line)
                self.matriz.extend(line)

        return self.matriz