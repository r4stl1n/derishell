class ConfigModel:

    def __init__(self):
        self.apiKey1 = ""
        self.apiSecret1 =  ""
        self.numOfOrders = 5
        self.contractSize = 100
        self.tradeInsturment = "BTC-PERPETUAL"
        self.basePrice = 0.0
        self.priceDistance = 0.0
        self.stopLossPrice = 0.0
        self.fcbMode = True
        self.apiUrl = "https://test.deribit.com"