from app import create_app, db
from app.models import User, Condominium
from flask import g

app = create_app()

with app.app_context():
    print(f"Total Users in DB: {User.query.count()}")
    
    # Explicitly check for nulls
    users_null = User.query.filter(User.condominium_id.is_(None)).all()
    print(f"Users with null condominium_id: {len(users_null)}")
    
    count = 0
    for user in users_null:
        if user.tenant:
            subdomain = user.tenant.lower().strip()
            condo = Condominium.query.filter_by(subdomain=subdomain).first()
            if condo:
                user.condominium_id = condo.id
                count += 1
                print(f"Linked {user.email} -> {condo.name}")
    
    if count > 0:
        db.session.commit()
        print(f"Updated {count} users.")
    else:
        print("No updates needed.")
