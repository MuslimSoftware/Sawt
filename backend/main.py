from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from features.chat.controllers.websocket_controller import router as websocket_router
from infrastructure.middlewares.exception_handler import global_exception_handler
import dspy
import os

async def lifespan(app: FastAPI):
    print("Starting up...")
    dspy.configure(
        lm=dspy.LM(
            model=os.getenv("AI_MODEL"),
            api_key=os.getenv("AI_API_KEY")
        )
    )
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
