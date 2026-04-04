from app.routes.url import generate_short_code

def test_generate_short_code_length(app):
    """
    Unit Tests? Don't test the whole app. Just test that Input A leads to Output B.
    Testing the standalone helper function in pure isolation to verify it successfully
    generates strings of the correct length without invoking any web routes.
    """
    with app.app_context():
        code = generate_short_code(length=8)
        assert len(code) == 8
        assert isinstance(code, str)
        
def test_generate_short_code_default_length(app):
    """Default length should be 6 characters."""
    with app.app_context():
        code = generate_short_code()
        assert len(code) == 6
