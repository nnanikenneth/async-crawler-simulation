from fastapi.middleware.cors import CORSMiddleware
# Used for testing...
CLIENT_TEST_URL = "http://localhost:3000"
def add_cors_middleware(app):
    app.add_middleware(CORSMiddleware,
        allow_origins=["*"], 
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
