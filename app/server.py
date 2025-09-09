import uvicorn


def main():
    """Launched with `poetry run start` at root level"""
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        app_dir="app",
    )


if __name__ == "__main__":
    main()
