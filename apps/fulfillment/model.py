from typing import Optional
import uuid
import datetime
from enum import Enum
from pydantic import BaseModel, Field

class FulfillmentRequest(BaseModel):
  id: str = Field(default_factory=uuid.uuid4, alias="_id")
  sender_id: str = Field(...)
  cosignee_id: str = Field(...)




#   FulfillmentRequest {
# 	_id
# 	sender_id - (a reference to a user_id)
# 	cosignee_id - (reference to a user_id)
# 	status [Accepted, InProgress, Completed, Cancelled]
# 	lineItems: [lineItemId1, lineItemId2, ...]
# 	pickUpLocation {
# 		addressLine1
# 		city
# 		state
# 		country
# 		PostalCode
# 	}
# 	dropOfLocation {
# 		addressLine1
# 		city
# 		state
# 		country
# 		PostalCode
# 	}
# 	cost - (of fulfilling the request)
# 	scheduledPickUpAt - data and time when the customer wan't their order to be picked up (How exact should this be?)
# 	expectedDeliveryDuration - (DateTime object)
# 	package {
# 		_id
# 		size {
# 			length
# 			height
# 			width
# 			categroy [very large, large, medium, small]
# 		}
# 		status [picking, picked, inTransit, delivered]
# 		packageRating
# 		packageReward
# 	}
# }
