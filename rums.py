from app import create_app, db
from app.models import Employee

app = create_app()
with app.app_context():
    anyaccounts = Employee.query.first()
    if anyaccounts is None:
        admin = Employee(username='admin', is_admin='y')
        admin.set_password('admin')
        db.session.add(admin)
        db.session.commit()

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'employee': employee}
