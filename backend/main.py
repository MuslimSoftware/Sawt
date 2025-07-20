from fastapi import FastAPI
from features.chat.controllers.websocket_controller import router as websocket_router
from infrastructure.middlewares.exception_handler import global_exception_handler

app = FastAPI()

# Middlewares
app.add_exception_handler(Exception, global_exception_handler)

# Routers
app.include_router(websocket_router)


@app.get("/")
async def root():
    return {"message": "Sawt Backend is running"}
