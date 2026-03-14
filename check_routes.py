from server import app
import json

routes = []
for route in app.routes:
    methods = list(getattr(route, "methods", []))
    path = getattr(route, "path", "")
    routes.append({"methods": methods, "path": path})

with open("routes_debug.json", "w", encoding="utf-8") as f:
    json.dump(routes, f, indent=2)
