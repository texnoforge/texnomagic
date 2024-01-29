import commontest  # common testing code


def test_abcs_basic():
    abcs = commontest.ABCS
    assert len(abcs.abcs) == 1, "only one abc should be loaded"

    abc = abcs.get_alphabet("DEFINITELY NOT EXISTING")
    assert abc is None

    abc = abcs.get_alphabet(commontest.ABC.name)
    assert abc.name == commontest.ABC.name
    assert abc.handle == commontest.ABC.handle

    abc = abcs.get_alphabet(commontest.ABC.handle)
    assert abc.name == commontest.ABC.name
    assert abc.handle == commontest.ABC.handle

    # test tag:abc selector
    abc_id = f'test:{commontest.ABC.name}'
    abc = abcs.get_alphabet(abc_id)
    assert abc.name == commontest.ABC.name
