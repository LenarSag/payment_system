MAX_USERNAME_LENGTH = 150
MAX_EMAIL_LENGTH = 150


SECRET_KEY = "django-insecure-!8f-ol^+wafcwyx7&h@7ldw8^5a6x_0i741uk+on*&0_%@h&%&"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 120000


TRANSACTION_KEY = "gfdmhghif38yrf9ew0jkf32"


# def upgrade():
#     # Insert test users
#     op.execute("""
#     INSERT INTO users (username, email, first_name, last_name, password, is_active, role)
#     VALUES
#     ('testuser1', 'testuser1@example.com', 'hashed_password1', true, user),
#     ('testuser2', 'testuser2@example.com', 'hashed_password2', true, false),
#     ('adminuser', 'admin@example.com', 'hashed_password_admin', true, true);
#     """)

# def downgrade():
#     # Delete test users
#     op.execute("""
#     DELETE FROM users WHERE username IN ('testuser1', 'testuser2', 'adminuser');
#     """)

# leo      | leo@leo.ru  | leo        | leo       | $2b$12$3D1f8osq1RSDwRoj4AwO5eyPC/hkEVxr..K3BwldLYoa4ltCdhp7C

# leo2     | leo2@leo.ru | leo        | leo       | $2b$12$dSD09mEhynUCapL.FGUM6eVUvTPHzYiGk82SZeArohqka1PmQhXse
