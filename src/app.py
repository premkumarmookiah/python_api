from fastapi import FastAPI, HTTPException
from src.schemas import PostCreate, PostResponse
from src.db import Post, create_db_and_tables, get_async_session
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifesapn(app: FastAPI):
    await create_db_and_tables()
    yield

app =  FastAPI(lifespan=lifesapn)






""" 
text_posts = {
    1: {
        "title": "Getting Started with FastAPI",
        "content": "FastAPI is a modern Python framework for building fast APIs with automatic documentation and async support."
    },
    2: {
        "title": "Why Developers Love Python",
        "content": "Python is popular because of its simple syntax, huge ecosystem, and versatility in backend, AI, automation, and scripting."
    },
    3: {
        "title": "Understanding REST APIs",
        "content": "REST APIs allow applications to communicate using standard HTTP methods like GET, POST, PUT, and DELETE."
    },
    4: {
        "title": "Benefits of Using PostgreSQL",
        "content": "PostgreSQL is a powerful open-source relational database known for reliability, performance, and advanced SQL features."
    },
    5: {
        "title": "How Async Programming Works",
        "content": "Async programming allows applications to handle multiple tasks efficiently without blocking the main execution thread."
    },
    6: {
        "title": "Introduction to Docker",
        "content": "Docker helps developers package applications and dependencies into portable containers that run consistently everywhere."
    },
    7: {
        "title": "Importance of Clean Code",
        "content": "Writing clean code improves readability, maintainability, and collaboration between developers in large projects."
    },
    8: {
        "title": "What is JWT Authentication",
        "content": "JWT authentication uses signed tokens to securely verify users between client and server applications."
    },
    9: {
        "title": "Understanding Git Branches",
        "content": "Git branches help developers work on features independently without affecting the main codebase."
    },
    10: {
        "title": "Why Learn SQL",
        "content": "SQL is essential for querying, managing, and analyzing structured data stored in relational databases."
    }
}

@app.get("/posts")
def get_all_posts(limit: int = None):
    if limit:
        return {k: text_posts[k] for i, k in enumerate(text_posts) if i < limit}
    return text_posts

@app.get("/posts/{id}")
def get_post(id: int):
    if id not in text_posts:
        raise HTTPException(status_code=404,detail="Post not found")
    return text_posts.get(id)


@app.post("/posts")
def create_post(post: PostCreate) -> PostResponse:
    new_post =  {"title":post.title, "content" : post.content}
    text_posts[max(text_posts.keys()) + 1] = new_post
    return text_posts """