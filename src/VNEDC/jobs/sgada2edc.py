import sys
import os
curPath = os.path.abspath(os.path.dirname(__file__))
rootPath = os.path.split(curPath)[0]
sys.path.append(rootPath)
from jobs.gdnbr_sgada import GDNBR, SgadaInterface
from datetime import datetime


class SGADA2EDC(object):
    plants = ""
    start_date = ""
    end_date = ""

    def __init__(self, start_date, end_date, plants):
        self.start_date = start_date
        self.end_date = end_date
        self.plants = plants

    def execute(self):
        plants = self.plants
        for plant in plants:
            sgada = SgadaInterface(plant, start_date, end_date)
            sgada.run()


plants = [GDNBR]
# start_date = "2024-07-01"
# end_date = "2024-07-09"
start_date = datetime.today().strftime('%Y-%m-%d')
end_date = datetime.today().strftime('%Y-%m-%d')
sgada = SGADA2EDC(start_date, end_date, plants)
sgada.execute()
