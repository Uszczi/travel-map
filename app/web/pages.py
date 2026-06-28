from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

from app.api.common import DEFAULT_START_X, DEFAULT_START_Y

router = APIRouter(tags=["Web"], include_in_schema=False)

ALGORITHMS = [
    ("random", "Random walk"),
    ("dfs", "Depth-first search"),
    ("astar", "A* (start \u2192 end)"),
    ("allstreet", "All streets"),
]


@router.get("/", response_class=HTMLResponse)
def index(request: Request) -> HTMLResponse:
    from app.web.templates import templates

    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "algorithms": ALGORITHMS,
            "default_x": DEFAULT_START_X,
            "default_y": DEFAULT_START_Y,
        },
    )
