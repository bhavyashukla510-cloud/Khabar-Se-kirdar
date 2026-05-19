from fastapi import APIRouter
from pydantic import BaseModel
import matplotlib.pyplot as plt
import uuid
import os

router = APIRouter(prefix="/infographics", tags=["Infographics"])

OUTPUT_DIR = "outputs/video"
os.makedirs(OUTPUT_DIR, exist_ok=True)


class ChartRequest(BaseModel):
    title: str
    labels: list
    values: list


@router.post("/")
def generate_chart(request: ChartRequest):

    filename = f"{uuid.uuid4()}.png"
    filepath = os.path.join(OUTPUT_DIR, filename)

    plt.figure(figsize=(8, 5))
    plt.bar(request.labels, request.values)
    plt.title(request.title)
    plt.savefig(filepath)
    plt.close()

    return {
        "success": True,
        "chart_url": f"/outputs/video/{filename}"
    }