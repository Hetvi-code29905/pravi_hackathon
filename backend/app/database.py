from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.config import settings

# Will be populated on startup
db_client: AsyncIOMotorClient = None


async def init_db():
    """Initialize MongoDB connection and Beanie ODM."""
    global db_client

    # Import all document models
    from app.models.infrastructure import InfrastructureClass
    from app.models.asset_type import AssetType
    from app.models.project import Project
    from app.models.asset import Asset
    from app.models.lifecycle import LifecycleTemplate, LifecycleEvent
    from app.models.condition import ConditionAssessment
    from app.models.inspection import Inspection
    from app.models.maintenance import MaintenanceRecord
    from app.models.issue import Issue
    from app.models.component import AssetComponent
    from app.models.document import AssetDocument
    from app.models.risk import RiskAssessment
    from app.models.cost import AssetCost
    from app.auth.models import User

    url = settings.MONGODB_URL
    client_kwargs = {}

    try:
        import certifi
        ca_file = certifi.where()
    except Exception:
        ca_file = None

    if "mongodb+srv" in url:
        client_kwargs["serverSelectionTimeoutMS"] = 5000
        client_kwargs["connectTimeoutMS"] = 5000
        client_kwargs["socketTimeoutMS"] = 5000
        if ca_file:
            client_kwargs["tlsCAFile"] = ca_file
        client_kwargs["tlsAllowInvalidCertificates"] = True

    try:
        db_client = AsyncIOMotorClient(url, **client_kwargs)
        # Test connection ping
        await db_client.admin.command('ping')
        print(f"[OK] Connected to MongoDB: {url[:30]}... / {settings.DATABASE_NAME}")
    except Exception as e:
        print(f"[WARN] Connection to {url[:30]} failed ({e}). Falling back to local MongoDB: mongodb://localhost:27017")
        url = "mongodb://localhost:27017"
        db_client = AsyncIOMotorClient(url, serverSelectionTimeoutMS=5000)
        await db_client.admin.command('ping')
        print(f"[OK] Connected to fallback local MongoDB: {settings.DATABASE_NAME}")

    await init_beanie(
        database=db_client[settings.DATABASE_NAME],
        document_models=[
            User,
            InfrastructureClass,
            AssetType,
            Project,
            Asset,
            LifecycleTemplate,
            LifecycleEvent,
            ConditionAssessment,
            Inspection,
            MaintenanceRecord,
            Issue,
            AssetComponent,
            AssetDocument,
            RiskAssessment,
            AssetCost,
        ],
    )
    print(f"[OK] Beanie initialized with {settings.DATABASE_NAME}")


async def close_db():
    """Close MongoDB connection."""
    global db_client
    if db_client:
        db_client.close()
        print("[INFO] MongoDB connection closed")
