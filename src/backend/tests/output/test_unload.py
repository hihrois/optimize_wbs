def add(a: int, b: int) -> int:
    return a + b


def test_add():
    assert add(2, 8) == 10


# 例外発生の確認
# def test_div_zero():
#     with pytest.raises(ZeroDivisionError):
#         div(10, 0)
