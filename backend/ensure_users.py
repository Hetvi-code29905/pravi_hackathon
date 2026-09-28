import asyncio
from app.database import init_db
from app.auth.models import User
from app.auth.utils import hash_password

async def main():
    await init_db()
    users_data = [
        {
            "email": "secretary@rnb.gujarat.gov.in",
            "username": "secretary@rnb.gujarat.gov.in",
            "password": "secretary123",
            "full_name": "Shri M. K. Das, IAS",
            "role": "SECRETARY",
            "department": "Roads & Buildings Department, Govt. of Gujarat",
            "designation": "Principal Secretary (R&B)",
        },
        {
            "email": "admin@rnb.gujarat.gov.in",
            "username": "admin@rnb.gujarat.gov.in",
            "password": "admin123",
            "full_name": "Shri Rajesh Patel (Chief Engineer)",
            "role": "ADMIN",
            "department": "Gujarat Roads & Buildings Department",
            "designation": "Chief Engineer & State Asset Director",
        },
        {
            "email": "engineer@rnb.gujarat.gov.in",
            "username": "engineer@rnb.gujarat.gov.in",
            "password": "engineer123",
            "full_name": "Er. Amit Shah",
            "role": "ENGINEER",
            "department": "Capital Project Division, Gandhinagar",
            "designation": "Executive Engineer",
        },
        {
            "email": "inspector@rnb.gujarat.gov.in",
            "username": "inspector@rnb.gujarat.gov.in",
            "password": "inspector123",
            "full_name": "Smt. Priya Desai",
            "role": "INSPECTOR",
            "department": "Quality Control & Inspection Wing",
            "designation": "Assistant Executive Engineer (QC)",
        },
        {
            "email": "contractor@rnb.gujarat.gov.in",
            "username": "contractor@rnb.gujarat.gov.in",
            "password": "contractor123",
            "full_name": "M/s L&T Infrastructure Engineering",
            "role": "CONTRACTOR",
            "department": "EPC Concessionaire Partner",
            "designation": "Authorized Signatory / Project Lead",
        },
    ]

    for ud in users_data:
        existing = await User.find_one(User.email == ud["email"])
        if not existing:
            u = User(
                username=ud["username"],
                email=ud["email"],
                password_hash=hash_password(ud["password"]),
                full_name=ud["full_name"],
                role=ud["role"],
                department=ud["department"],
                designation=ud["designation"],
            )
            await u.insert()
            print(f"Created user: {ud['email']}")
        else:
            print(f"User already exists: {ud['email']}")

    all_users = await User.find_all().to_list()
    print("ALL REGISTERED USERS IN DB:")
    for u in all_users:
        print(f" - {u.email} ({u.role})")

if __name__ == "__main__":
    asyncio.run(main())
