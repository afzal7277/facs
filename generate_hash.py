from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# admin_password = "admin123"

# admin_hashed = pwd_context.hash(admin_password)
# print(admin_hashed)

# $2b$12$5zJj7CA69mQ5.Qd6T0A69uuH0apGxU8skrlgkYM6VQdfVyvQ6LSHW

# cell_password = "cell123"

# cell_hashed = pwd_context.hash(cell_password)
# print(cell_hashed)

# $2b$12$fsvFpmpyE89o.GGYkh8VKOUHC1nFrPVr/pBB4KXnSWszqmby2LDaq

# forklift_password = "forklift123"

# forklift_hashed = pwd_context.hash(forklift_password)
# print(forklift_hashed)

# $2b$12$WTiY4b/fl8e5qjxaufMemu.0JCRZf0KjkXJMl82mTGwfMM8fDGwbC

# forklift1_password = "forklift1234"

# forklift1_hashed = pwd_context.hash(forklift1_password)
# print(forklift1_hashed)

# $2b$12$qRX2BfIjqUwn9ybJYCxQg.xJxoIRDCHa/6OA8036nqRcVFVAY07gO