from ninja_extra import NinjaExtraAPI
from ninja_jwt.controller import NinjaJWTDefaultController

api = NinjaExtraAPI(
    title="Skinask API",
    version="0.0.1",
)

api.register_controllers(NinjaJWTDefaultController)
api.auto_discover_controllers()
