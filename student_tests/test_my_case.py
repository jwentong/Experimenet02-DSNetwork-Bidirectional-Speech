from src.connections import connect_pair, disconnect_pair
from src.models import Endpoint

class TableObj:
    def __init__(self):
        self.T = [dict(), dict()]
        self.S = {}
        self.pairs = {}
        self.t_maps = {
            0: {},
            1: {}
        }
        self.s_map = {}

def test_double_disconnect():
    tables = TableObj()
    a = Endpoint(0,1)
    b = Endpoint(1,2)
    assert connect_pair("conn1", a, b, tables) == True

    assert disconnect_pair("conn1", tables) == True
    assert disconnect_pair("conn1", tables) == False