from frontend.main import create_app


def test_frontend_main_exposes_launch():
    app = create_app()
    assert app is not None
