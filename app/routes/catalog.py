from fastapi import APIRouter, Depends, HTTPException, status

router = APIRouter(prefix="/catalog", tags=["Catalogs"])


@router.get("/location_type")
def get_location_type():
    return [
        {"key": "factory",
         "label": "Nhà máy"},
        {"key": "residence",
         "label": "Khu nhà ở"},
        {"key": "private_house",
         "label": "Nhà riêng"}
    ]
