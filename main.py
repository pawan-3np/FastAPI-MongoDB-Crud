from fastapi import FastAPI, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from models import UserModel, PyObjectId
from typing import List

app = FastAPI()

MongoDB_URL = "mongodb+srv://pawanmagapalli_db_user:GivIjRJewpiU3wXF@cluster0.uvidgbt.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

client = AsyncIOMotorClient(MongoDB_URL)
database = client.users_db
user_collection = database.get_collection("users_collection")


# Helper to convert MongoDB document to dict
def user_helper(user) -> dict:
    return {
        "id": str(user["_id"]),
        "name": user["name"],
        "email": user["email"],
    }


# ✅ Create user
@app.post("/users", response_model=UserModel)
async def create_user(user: UserModel):
    user = user.dict(by_alias=True)
    user.pop("id", None)
    new_user = await user_collection.insert_one(user)
    created_user = await user_collection.find_one({"_id": new_user.inserted_id})
    return user_helper(created_user)


# ✅ Get user by ID
@app.get("/users/{id}", response_model=UserModel)
async def get_user(id: str):
    if not PyObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid user ID")

    user = await user_collection.find_one({"_id": PyObjectId(id)})
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user_helper(user)


# ✅ Update user by ID
@app.put("/users/{id}", response_model=UserModel)
async def update_user(id: str, user: UserModel):
    if not PyObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid user ID")

    user_dict = user.dict(by_alias=True)
    user_dict.pop("_id", None)  # Prevent changing _id

    result = await user_collection.update_one(
        {"_id": PyObjectId(id)}, {"$set": user_dict}
    )

    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="User not found or no changes made")

    updated_user = await user_collection.find_one({"_id": PyObjectId(id)})
    return user_helper(updated_user)


# ✅ Delete user by ID
@app.delete("/users/{id}")
async def delete_user(id: str):
    if not PyObjectId.is_valid(id):
        raise HTTPException(status_code=400, detail="Invalid user ID")

    delete_result = await user_collection.delete_one({"_id": PyObjectId(id)})

    if delete_result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")

    return {"message": "User deleted successfully"}
