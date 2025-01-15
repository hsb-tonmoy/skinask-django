from ninja_extra import NinjaExtraAPI
from ninja_jwt.controller import NinjaJWTSlidingController

api = NinjaExtraAPI(
    title="Skinask API",
    version="0.0.1",
)

api.register_controllers(NinjaJWTSlidingController)
api.auto_discover_controllers()
