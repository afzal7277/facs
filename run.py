import uvicorn

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)


# 127.0.0.1 = only your PC

# 0.0.0.0 = accessible from other devices (your phone)
