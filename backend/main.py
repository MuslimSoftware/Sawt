from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from features.chat.controllers.websocket_controller import router as websocket_router
from infrastructure.middlewares.exception_handler import global_exception_handler
import dspy
import os

dspy.configure(
    lm=dspy.LM(
        model=os.getenv("AGENT_MODEL"),
        api_key=os.getenv("AGENT_API_KEY")
    )
)

async def lifespan(app: FastAPI):
    print("Starting up...")
    yield
    print("Shutting down...")

app = FastAPI(lifespan=lifespan)

# Middlewares
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(Exception, global_exception_handler)

# Routers
app.include_router(websocket_router)


@app.get("/")
async def root():
    return {"message": "Sawt Backend is running"}
