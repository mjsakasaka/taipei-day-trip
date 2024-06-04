from fastapi import *
from fastapi.responses import FileResponse
from apps.attractions import attrac
from apps.mrt import mrt
from apps.user import user
import uvicorn
app = FastAPI()

# Static Pages (Never Modify Code in this Block)
@app.get("/", include_in_schema=False)
async def index(request: Request):
	return FileResponse("./static/index.html", media_type="text/html")
@app.get("/attraction/{id}", include_in_schema=False)
async def attraction(request: Request, id: int):
	return FileResponse("./static/attraction.html", media_type="text/html")
@app.get("/booking", include_in_schema=False)
async def booking(request: Request):
	return FileResponse("./static/booking.html", media_type="text/html")
@app.get("/thankyou", include_in_schema=False)
async def thankyou(request: Request):
	return FileResponse("./static/thankyou.html", media_type="text/html")

app.include_router(attrac)
app.include_router(mrt)
app.include_router(user)


if __name__ == '__main__':
    uvicorn.run("app:app", port=8000, reload=True, host='0.0.0.0')