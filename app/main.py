from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from examples.graph_example import ExampleGraph

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


@app.get("/example")
async def example_root(input: str):
    agent = ExampleGraph()
    response = await agent.run(input)
    return response
