async def init_db():
    """Initialize JSON storage directories"""
    import os
    os.makedirs("data_storage", exist_ok=True)
    print("JSON storage ready")

async def get_session():
    class DummySession:
        async def __aenter__(self):
            return None
        async def __aexit__(self, *args):
            pass
    yield DummySession()
