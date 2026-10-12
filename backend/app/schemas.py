from pydantic import BaseModel, ConfigDict, Field, StrictBool, model_validator


class DeliveryIn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str = Field(min_length=1, max_length=20)
    location_id: str = Field(min_length=1, max_length=50)


class OptimizeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    depot_id: str = Field(min_length=1, max_length=50)
    return_to_depot: StrictBool
    deliveries: list[DeliveryIn] = Field(min_length=1, max_length=8)

    @model_validator(mode="after")
    def delivery_ids_must_be_unique(self):
        ids = [d.id for d in self.deliveries]
        if len(ids) != len(set(ids)):
            raise ValueError("Delivery IDs must be unique")
        return self


class OptimizeResponse(BaseModel):
    ordered_delivery_ids: list[str]
    total_distance_km: float
    driving_time_minutes: float
    depot_id: str
    return_to_depot: bool
    assumptions: list[str]


class ParseDeliveryIn(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str = Field(min_length=1, max_length=20)
    text: str = Field(min_length=1, max_length=300)


class ParseRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    deliveries: list[ParseDeliveryIn] = Field(min_length=1, max_length=8)
    instructions: str = Field(default="", max_length=1000)
