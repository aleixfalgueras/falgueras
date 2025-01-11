CREATE TABLE testing.students_daily (
    name STRING,
    surname STRING,
    age INT,
    birth_date DATE NOT NULL
)
PARTITION BY birth_date;