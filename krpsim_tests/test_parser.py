import sys
sys.path.append('..')
from krpsim_setting import Setting  # noqa: E402


def stock_tester(expression):
    try:
        setting = Setting()
        setting.parse_stock(expression)
        return (setting.initial_place_tokens)
    except Exception as e:
        return(e.__str__())


def optimize_tester(expression):
    try:
        setting = Setting()
        setting.parse_optimize(expression)
        return (setting.optimize)
    except Exception as e:
        return(e.__str__())


def test_stock_empty():
    res = stock_tester(":")
    assert res == "Stock Error: Invalid stock name format"


def test_stock_without_quantity():
    res = stock_tester("planche:")
    assert res == "Stock Error: Quantity should be a valid integer"


def test_stock_no_name():
    res = stock_tester(":8")
    print(res)
    assert res == "Stock Error: Invalid stock name format"


def test_stock_not_integer():
    res = stock_tester("planche:dd")
    assert res == "Stock Error: Quantity should be a valid integer"


def test_stock_multiple():
    res = stock_tester("planche:8:8")
    assert res == "Stock Error: Invalid stock format"


def test_stock_multiple_empty():
    res = stock_tester("planche::8")
    assert res == "Stock Error: Invalid stock format"


def test_stock_multiple_empty_2():
    res = stock_tester("planche::8::8")
    assert res == "Stock Error: Invalid stock format"


def test_stock_multiple_empty_3():
    res = stock_tester("::")
    assert res == "Stock Error: Invalid stock format"


def test_stock_invalid_separator():
    res = stock_tester(";")
    assert res == "Stock Error: Invalid stock format"


def test_stock_weird_name():
    res = stock_tester("[[];[p;lo]]:8")
    assert str(res) == '''{'[[];[p;lo]]': 8}'''


def test_stock_same_name():
    try:
        setting = Setting()
        setting.parse_stock("planche:8")
        setting.parse_stock("planche:7")
        res = setting.initial_place_tokens
    except Exception as e:
        res = e.__str__()
    assert str(res) == "{'planche': 7}"


def test_optimize_simple():
    res = optimize_tester("optimize:(time;armoire)")
    assert str(res) == '''['time', 'armoire']'''


def test_optimize_empty():
    res = optimize_tester(":")
    assert str(res) == 'Optimize Error : Invalid optimize format'


def test_optimize_without_value():
    res = optimize_tester("optimize:")
    assert str(res) == 'Optimize Error : Invalid optimize format'


def test_optimize_without_name():
    res = optimize_tester(":(time;armoire)")
    assert str(res) == 'Optimize Error : Invalid optimize name format'


def test_optimize_multiple():
    res = optimize_tester("optimize:(time;armoire):(time;armoire)")
    assert str(res) == 'Optimize Error : Invalid optimize format'


def test_optimize_multiple_2():
    res = optimize_tester("optimize::(time;armoire)")
    assert str(res) == 'Optimize Error : Invalid optimize name format'


def test_optimize_multiple_3():
    res = optimize_tester("optimize::(time;armoire)::(time;armoire)")
    assert str(res) == 'Optimize Error : Invalid optimize format'


def test_optimize_invalid_separator():
    res = optimize_tester("optimize;(time;armoire)")
    assert str(res) == 'Optimize Error : Invalid optimize format'


def test_optimize_weird_value():
    res = optimize_tester("optimize:(d][][][];armoire)")
    assert str(res) == '''['d][][][]', 'armoire']'''


def test_optimize_weird_value_2():
    res = optimize_tester("optimize:(time;armoire)()")
    assert str(res) == '''['time', 'armoire)(']'''


def test_optimize_weird_value_3():
    res = optimize_tester("optimize:((time;armoire)")
    assert str(res) == '''['(time', 'armoire']'''
