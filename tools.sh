# generate migration automatically
alembic revision --autogenerate -m "add new column or table"

# example: alembic revision --autogenerate -m "add phoneNumber to Employee"


alembic upgrade head
