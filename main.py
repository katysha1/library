import psycopg2

conn = psycopg2.connect(
    dbname="postgres",
    user="postgres",
    password="1234",
    host="localhost",
    port="5432"
)
print("Подключение к Базе данных успешно выполнено")
cur = conn.cursor()

#def main():

# if __name__ == "__main__":
    # main()

cur.close()
conn.close()
print("Подключение закрыто")

