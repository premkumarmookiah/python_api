from fastapi import FastAPI, HTTPException, File, UploadFile, Form, Depends
from imagekitio.types import FileUploadResponse
from src.schemas import PostCreate, PostResponse, UserCreate,UserRead,UserUpdate
from src.db import Post, create_db_and_tables, get_async_session,User
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from sqlalchemy import select
from src.images import imagekit
from pathlib import Path
# from imagekitio.models.UploadFileRequestOptions import UploadFileRequestOptions
import shutil
import os
import uuid
import tempfile
from src.users import auth_backend, current_active_user, fastapi_users
from sqlalchemy.orm import selectinload

@asynccontextmanager
async def lifesapn(app: FastAPI):
    await create_db_and_tables()
    yield

app =  FastAPI(lifespan=lifesapn)

app.include_router(fastapi_users.get_auth_router(auth_backend),prefix="/auth/jwt",tags=["auth"])
app.include_router(fastapi_users.get_register_router(UserRead,UserCreate),prefix="/auth",tags=["auth"])
app.include_router(fastapi_users.get_reset_password_router(),prefix="/auth",tags=["auth"])
app.include_router(fastapi_users.get_verify_router(UserRead),prefix="/auth",tags=["auth"])
app.include_router(fastapi_users.get_users_router(UserRead, UserUpdate),prefix="/users",tags=["users"])

@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    caption: str = Form(""),
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session)
):
    temp_file_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
            temp_file_path = temp_file.name
            shutil.copyfileobj(file.file, temp_file)
         
        # Upload from file
        upload_result: FileUploadResponse = imagekit.files.upload(
        file=Path(temp_file_path),
        file_name=file.filename,
        use_unique_file_name=True,
        # folder="/products",
        tags=["backend-upload"]
        )
        
        file_id = upload_result.file_id
        url = upload_result.url
        post = Post(
            caption = caption,
            user_id = user.id,
            url = url,
            file_type = "video" if file.content_type.startswith("video/") else "image" ,
            file_name = upload_result.name
        )
        session.add(post)
        await session.commit()
        await session.refresh(post)
        return post
    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
        file.file.close()

        

@app.get("/feed")
async def get_feed(
    user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_async_session)
):
    result = await session.execute(select(Post).options(selectinload(Post.user)).order_by(Post.created_at.desc()))
    posts = [row[0] for row in result.all()]

    posts_data = []
    for post in posts:
        posts_data.append(
            {
                "id": str(post.id),
                "user_id": str(post.user_id),
                "caption": post.caption,
                "url": post.url,
                "file_type": post.file_type,
                "file_name": post.file_name,
                "created_at": post.created_at.isoformat(),
                "is_owner": post.user_id == user.id,
                "email": post.user.email if post.user else None
            }
        )
    return {"posts": posts_data}

@app.delete("/posts/{post_id}")
async def delete_post(post_id: str, session: AsyncSession = Depends(get_async_session),user: User = Depends(current_active_user),):
    try:
        post_uuid = uuid.UUID(post_id)

        result = await session.execute(select(Post).where(Post.id == post_uuid))
        post_data = result.scalars().first()

        if not post_data:
            raise HTTPException(status_code=404,detail="Post not found") 
        
        if post_data.user_id != user.id:
            raise HTTPException(status_code=403,detail="You don't have permission to delete this post")
        
        await session.delete(post_data)
        await session.commit()
        return {"success": True, "message": "Post deleted successfully"}

    except Exception as e:
        raise HTTPException(status_code=500,detail=str(e))