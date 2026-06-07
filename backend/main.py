# main.py - CLI tương tác với chatbot
import asyncio
from data import database as db
from agents import chatbot, skill_registry


async def run_interactive():
    print("\n" + "=" * 60)
    print("   CHATBOT AI NOI BO")
    print("=" * 60)

    print("\nDanh sach tai khoan:")
    for emp in db.get_all_employees():
        print(f"  - ID: {emp['user_id']:<8} | Ten: {emp['name']:<15} | Role: {emp['role'].upper()}")

    user_id = ""
    while not user_id:
        uid = input("\nNhap User ID: ").strip()
        if db.check_user_exists(uid):
            user_id = uid
        else:
            print("ID khong ton tai.")

    user_info = db.get_user_info_safe(user_id)
    name = user_info["name"]
    role = user_info["role"]
    print(f"\nDang nhap: {name} ({role.upper()})")
    print("Gõ /skills de xem skills, 'exit' de thoat.")
    print("-" * 60)

    while True:
        try:
            query = input(f"\n{name} > ").strip()
            if not query:
                continue
            if query.lower() in ["exit", "quit"]:
                print("Tam biet!")
                break

            if query.lower() == "/skills":
                skills = skill_registry.list_all()
                print(f"\nSkills ({len(skills)}):")
                for s in skills:
                    print(f"  - {s.name}: {s.description}")
                continue

            result = await chatbot.ainvoke({
                "user_id": user_id,
                "user_name": name,
                "query": query,
                "agent_response": ""
            })
            print(f"\nBot: {result['agent_response']}")

        except KeyboardInterrupt:
            print("\nTam biet!")
            break
        except Exception as e:
            print(f"Loi: {e}")


if __name__ == "__main__":
    asyncio.run(run_interactive())
