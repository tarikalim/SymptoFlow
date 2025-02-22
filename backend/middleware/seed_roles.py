from backend.model import db
from backend.model.model import Role


def seed_roles():
    roles = ["doctor", "patient"]
    for role_name in roles:
        existing_role = Role.query.filter_by(name=role_name).first()
        if not existing_role:
            new_role = Role(name=role_name)
            db.session.add(new_role)
    try:
        db.session.commit()
        print("Roles seeded successfully.")
    except Exception as e:
        db.session.rollback()
        print(f"Error seeding roles: {e}")