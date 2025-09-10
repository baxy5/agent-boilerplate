from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.endpoints import graph_example_route

app = FastAPI()

# Example origins
origins = ["http://localhost:3000", "http://localhost:4200"]

app.add_middleware(
  CORSMiddleware,
  allow_origins=origins,
  allow_credentials=True,
  allow_methods=["GET", "POST"],
  allow_headers=["*"],
)


@app.get("/")
def read_root():
  return {"Hello": "World"}


app.include_router(graph_example_route.router, prefix="/example", tags=["Examples"])
