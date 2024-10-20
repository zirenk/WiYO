from sqlalchemy import inspect
from app import app, db
from models import User, Poll, Response

def display_schema():
    with app.app_context():
        inspector = inspect(db.engine)
        
        for table_name in inspector.get_table_names():
            print(f"\nTable: {table_name}")
            print("-" * (len(table_name) + 7))
            
            columns = inspector.get_columns(table_name)
            for column in columns:
                print(f"  - {column['name']} ({column['type']})")
                
            primary_key = inspector.get_pk_constraint(table_name)
            if primary_key['constrained_columns']:
                print(f"  Primary Key: {', '.join(primary_key['constrained_columns'])}")
            
            foreign_keys = inspector.get_foreign_keys(table_name)
            for fk in foreign_keys:
                print(f"  Foreign Key: {', '.join(fk['constrained_columns'])} -> {fk['referred_table']}.{', '.join(fk['referred_columns'])}")

if __name__ == "__main__":
    display_schema()
