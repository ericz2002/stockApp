import main

def test_verify_password():
    assert main.verify_password("u1", "c5ea71554c774daf7fab320fc3476afc0617eb00") == True
    