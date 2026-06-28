from fastapi.templating import Jinja2Templates

from app.utils import ROOT_PATH

# Server-rendered page/partial templates live under templates/web/.
# (Email templates under templates/<locale>/email/ are handled separately
# by fastapi-mail and are intentionally not exposed here.)
templates = Jinja2Templates(directory=str(ROOT_PATH / "templates" / "web"))
