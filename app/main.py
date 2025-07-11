from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.v1.endpoints.old_apart_table import router as old_apart_routrer 
from api.v1.endpoints.main_endpoints import router as main_router 

app = FastAPI()



app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173",
                   "https://up.dsa.mlc.gov/",
                   "http://10.9.96.160:5154"],  # или ["*"] для всех
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(old_apart_routrer)
app.include_router(main_router)