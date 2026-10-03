from checkout import total
import pytest
@pytest.mark.parametrize("discount",[0,1,15,50,100])
def test_percent(discount):
    assert total([12,38],discount)==pytest.approx(50*(1-discount/100))
@pytest.mark.parametrize("discount",[-1,101])
def test_invalid(discount):
    with pytest.raises(ValueError): total([10],discount)
