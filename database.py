from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase, AsyncIOMotorCollection
from typing import Optional
import logging

logger = logging.getLogger(name=__name__)


class MongoDB:
    client: Optional[AsyncIOMotorClient] = None
    db: Optional[AsyncIOMotorDatabase] = None

    @classmethod
    async def connect_db(cls) -> None:
        """Connect to MongoDB"""
        try:
            cls.client = AsyncIOMotorClient(host="mongodb://localhost:27017")
            cls.db = cls.client["lumi_db"]

            # Test connection
            await cls.client.admin.command(command='ping')
            logger.info(msg=f"Connected to MongoDB: lumi_db")
        except Exception as e:
            logger.error(msg=f"Failed to connect to MongoDB: {e}")
            raise

    @classmethod
    async def close_db(cls) -> None:
        """Close MongoDB connection"""
        if cls.client:
            cls.client.close()
            logger.info(msg="MongoDB connection closed")

    @classmethod
    def get_db(cls) -> AsyncIOMotorDatabase:
        """Get database instance"""
        if cls.db is None:
            raise RuntimeError("MongoDB not connected. Call connect_db() first.")
        return cls.db


# Database collections
def get_sessions_collection() -> AsyncIOMotorCollection:
    return MongoDB.get_db()["sessions"]


def get_messages_collection() -> AsyncIOMotorCollection:
    return MongoDB.get_db()["messages"]


def get_short_term_memory_collection() -> AsyncIOMotorCollection:
    return MongoDB.get_db()["short_term_memory"]


def get_progress_collection() -> AsyncIOMotorCollection:
    return MongoDB.get_db()["student_progress"]


def get_questions_collection() -> AsyncIOMotorCollection:
    return MongoDB.get_db()["questions"]


def get_quiz_sessions_collection() -> AsyncIOMotorCollection:
    return MongoDB.get_db()["quiz_sessions"]


def get_subjects_collection() -> AsyncIOMotorCollection:
    return MongoDB.get_db()["subjects"]


def get_curriculum_collection() -> AsyncIOMotorCollection:
    return MongoDB.get_db()["curriculum"]

def get_quizzes_collection() -> AsyncIOMotorCollection:
    return MongoDB.get_db()["quizzes"]