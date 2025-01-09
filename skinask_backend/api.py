from ninja_extra import NinjaExtraAPI

api = NinjaExtraAPI(
    title="Skinask API",
    version="0.0.1",
)

api.auto_discover_controllers()
