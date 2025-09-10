from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from app.api.endpoints import graph_example_route
from app.services.env_config_service import get_env_configs


@asynccontextmanager
async def lifespan(_app: FastAPI):
  settings = get_env_configs()

  base_url = settings.postgres_url.unicode_string()
  connection_string = f"{base_url}?options=-c%20search_path%3Dlanggraph"

  async with AsyncPostgresSaver.from_conn_string(connection_string) as saver:
    await saver.setup()
    _app.state.checkpointer = saver
    yield


app = FastAPI(lifespan=lifespan)

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
