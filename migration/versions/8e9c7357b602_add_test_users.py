"""add test users

Revision ID: 8e9c7357b602
Revises: 6fc21982d838
Create Date: 2024-07-25 10:29:28.825204

"""
from typing import Sequence, Union
import uuid

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8e9c7357b602'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Insert test users into the person table and get their IDs
    person1_id = str(uuid.uuid4())
    person2_id = str(uuid.uuid4())

    op.execute(f"""
    INSERT INTO person (id, username, email, first_name, last_name, password, is_active, role, created_at)
    VALUES
    ('{person1_id}', 'testuser1', 'testuser1@test.com', 'Test', 'User1', '$2b$12$3D1f8osq1RSDwRoj4AwO5eyPC/hkEVxr..K3BwldLYoa4ltCdhp7C', true, 'user', NOW()),
    ('{person2_id}', 'testuser2', 'testuser2@test.com', 'Test', 'User2', '$2b$12$3D1f8osq1RSDwRoj4AwO5eyPC/hkEVxr..K3BwldLYoa4ltCdhp7C', true, 'admin', NOW());
    """)

    # Insert the corresponding records into the user and admin tables
    op.execute(f"""
    INSERT INTO "user" (person_id) VALUES ('{person1_id}');
    """)
    op.execute(f"""
    INSERT INTO "admin" (person_id) VALUES ('{person2_id}');
    """)


def downgrade() -> None:
    # Delete the inserted records
    op.execute("""
    DELETE FROM "user" WHERE person_id IN (SELECT id FROM person WHERE username IN ('testuser1'));
    DELETE FROM "admin" WHERE person_id IN (SELECT id FROM person WHERE username IN ('testuser2'));
    DELETE FROM person WHERE username IN ('testuser1', 'testuser2');
    """)
