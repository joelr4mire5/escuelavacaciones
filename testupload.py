import psycopg2

# Database connection URL
DATABASE_URL = "postgres://uehj6l5ro2do7e:pec2874786543ef60ab195635730a2b11bd85022c850ca40f1cda985eef6374fd@c952v5ogavqpah.cluster-czrs8kj4isg7.us-east-1.rds.amazonaws.com:5432/d8bh6a744djnub"

# Complete data for insertion
data = [
('6-8','Versículo','Jeremías 29:11',5),
('6-8','Versículo','Efesios 2:10',5),
('6-8','Versículo','Romanos 8:28',5),
('6-8','Versículo','Isaías 55:8',5),
('6-8','Versículo','Efesios 1:4',5),
('6-8','Versículo','Efesios 1:11',5),
('6-8','Versículo','Romanos 11:33',5),
('6-8','Versículo','Proverbios 3:19',5),
('6-8','Versículo','Isaías 40:28',5),
('6-8','Versículo','Salmo 147:5',5),
('6-8','Versículo','Job 12:13',5),
('6-8','Versículo','Santiago 1:5',5),
('6-8','Versículo','Apocalipsis 19:6',5),
('6-8','Versículo','1 Juan 5:4',5),
('6-8','Versículo','1 Crónicas 29:11',5),
('6-8','Versículo','1 Corintios 15:57',5),
('6-8','Versículo','2 Corintios 2:14',5),
('6-8','Versículo','Filipenses 4:13',5),
('6-8','Versículo','Isaías 41:10',5),
('6-8','Versículo','Salmos 9:10',5),
('6-8','Versículo','Salmos 28:7',5),
('6-8','Versículo','Salmos 91:2',5),
('6-8','Versículo','Salmos 37:4-5',5),
('6-8','Versículo','Proverbios 3:5-6',5),
('6-8','Versículo','Salmos 89:8',5),
('6-8','Versículo','Sofonías 3:17',5),
('6-8','Versículo','Jeremías 32:17',5),
('6-8','Versículo','Mateo 19:26',5),
('6-8','Versículo','Salmos 62:11',5),
('6-8','Versículo','Génesis 17:1',5),

('9-11','Versículo','Jeremías 29:1',5),
('9-11','Versículo','Efesios 2:10',5),
('9-11','Versículo','Romanos 8:28',5),
('9-11','Versículo','Isaías 55:8',5),
('9-11','Versículo','Efesios 1:4',5),
('9-11','Versículo','Efesios 1:11',5),
('9-11','Versículo','Romanos 11:33',5),
('9-11','Versículo','Proverbios 3:19',5),
('9-11','Versículo','Isaías 40:28',5),
('9-11','Versículo','Salmo 147:5',5),
('9-11','Versículo','Job 12:13',5),
('9-11','Versículo','Santiago 1:5',5),
('9-11','Versículo','Apocalipsis 19:6',5),
('9-11','Versículo','1 Juan 5:4',5),
('9-11','Versículo','1 Crónicas 29:11',5),
('9-11','Versículo','1 Corintios 15:57',5),
('9-11','Versículo','2 Corintios 2:14',5),
('9-11','Versículo','Filipenses 4:13',5),
('9-11','Versículo','Isaías 41:10',5),
('9-11','Versículo','Salmos 9:10',5),
('9-11','Versículo','Salmos 28:7',5),
('9-11','Versículo','Salmos 91:2',5),
('9-11','Versículo','Salmos 37:4-5',5),
('9-11','Versículo','Proverbios 3:5-6',5),
('9-11','Versículo','Salmos 89:8',5),
('9-11','Versículo','Sofonías 3:17',5),
('9-11','Versículo','Jeremías 32:17',5),
('9-11','Versículo','Mateo 19:26',5),
('9-11','Versículo','Salmos 62:11',5),
('9-11','Versículo','Génesis 17:1',5),

('4-5','Versículo','Jeremías 29:11a',5),
('4-5','Versículo','Efesios 2:10a',5),
('4-5','Versículo','Romanos 8:28a',5),
('4-5','Versículo','Isaías 55:8',5),
('4-5','Versículo','Proverbios 19:21',5),
('4-5','Versículo','2 Reyes 12:2a',5),
('4-5','Versículo','Proverbios 2:6',5),
('4-5','Versículo','Proverbios 3:19',5),
('4-5','Versículo','Isaías 40:28b',5),
('4-5','Versículo','Salmo 147:5',5),
('4-5','Versículo','Job 12:13',5),
('4-5','Versículo','Santiago 1:5a',5),
('4-5','Versículo','Apocalipsis 19:6b',5),
('4-5','Versículo','1 Juan 5:4',5),
('4-5','Versículo','1 Crónicas 29:11a',5),
('4-5','Versículo','1 Corintios 15:57',5),
('4-5','Versículo','2 Corintios 2:14a',5),
('4-5','Versículo','Filipenses 4:13',5),
('4-5','Versículo','Isaías 41:10a',5),
('4-5','Versículo','Salmos 28:7a',5),
('4-5','Versículo','Salmos 91:2',5),
('4-5','Versículo','Salmos 37:5',5),
('4-5','Versículo','Proverbios 3:5',5),
('4-5','Versículo','Salmos 89:8b',5),
('4-5','Versículo','Sofonías 3:17a',5),
('4-5','Versículo','Jeremías 32:17a',5),
('4-5','Versículo','Mateo 19:26',5),
('4-5','Versículo','Salmos 62:11',5),
('4-5','Versículo','Génesis 17:1b',5),

('0-3','Versículo','Jeremías 29:11a',5),
('0-3','Versículo','Efesios 2:10a',5),
('0-3','Versículo','Romanos 8:28a',5),
('0-3','Versículo','Isaías 55:8',5),
('0-3','Versículo','Proverbios 19:21',5),
('0-3','Versículo','2 Reyes 12:2a',5),
('0-3','Versículo','Proverbios 2:6',5),
('0-3','Versículo','Proverbios 3:19',5),
('0-3','Versículo','Isaías 40:28b',5),
('0-3','Versículo','Salmo 147:5',5),
('0-3','Versículo','Job 12:13',5),
('0-3','Versículo','Santiago 1:5a',5),
('0-3','Versículo','Apocalipsis 19:6b',5),
('0-3','Versículo','1 Juan 5:4',5),
('0-3','Versículo','1 Crónicas 29:11a',5),
('0-3','Versículo','1 Corintios 15:57',5),
('0-3','Versículo','2 Corintios 2:14a',5),
('0-3','Versículo','Filipenses 4:13',5),
('0-3','Versículo','Isaías 41:10a',5),
('0-3','Versículo','Salmos 28:7a',5),
('0-3','Versículo','Salmos 91:2',5),
('0-3','Versículo','Salmos 37:5',5),
('0-3','Versículo','Proverbios 3:5',5),
('0-3','Versículo','Salmos 89:8b',5),
('0-3','Versículo','Sofonías 3:17a',5),
('0-3','Versículo','Jeremías 32:17a',5),
('0-3','Versículo','Mateo 19:26',5),
('0-3','Versículo','Salmos 62:11',5),
('0-3','Versículo','Génesis 17:1b',5),

('12+','Versículo','2 Crónicas 24:1-2',5),
('12+','Versículo','Jeremías 29:11-13',5),
('12+','Versículo','Efesios 2:8-10',5),
('12+','Versículo','Romanos 8:28',5),
('12+','Versículo','Isaías 55:8-9',5),
('12+','Versículo','Proverbios 3:5-7',5),
('12+','Versículo','Romanos 11:33-36',5),
('12+','Versículo','Salmos 89:8-9',5),
('12+','Versículo','Isaías 40:28-31',5),
('12+','Versículo','Salmo 147:4-5',5),
('12+','Versículo','Job 12:13',5),
('12+','Versículo','Santiago 1:5-6',5),
('12+','Versículo','Apocalipsis 19:6-7',5),
('12+','Versículo','1 Juan 5:4',5),
('12+','Versículo','1 Crónicas 29:11-13',5),
('12+','Versículo','1 Corintios 15:57-58',5),
('12+','Versículo','2 Corintios 2:14',5),
('12+','Versículo','Salmos 18:1-2',5),
('12+','Versículo','Isaías 41:10',5),
('12+','Versículo','Salmos 9:10',5),
('12+','Versículo','Salmos 28:7',5),
('12+','Versículo','Salmos 91:2',5),
('12+','Versículo','Salmos 37:4-5',5),
('12+','Versículo','Proverbios 3:5-6',5),
('12+','Versículo','Jeremías 17:7-8',5),
('12+','Versículo','Sofonías 3:17',5),
('12+','Versículo','Jeremías 32:17-18',5),
('12+','Versículo','Mateo 19:26',5),
('12+','Versículo','Apocalipsis 11:17',5),
('12+','Versículo','1 Timoteo 1:97',5),

('12+','Capítulo','Isaias 40',155),
('12+','Capítulo','Salmos 91:2',80),
('0-3','Capítulo','Salmos 121',40),
('4-5','Capítulo','Salmos 121',40),
('6-8','Capítulo','Salmos 46',55),
('6-8','Capítulo','Salmos 145',105),
('9-11','Capítulo','Salmos 46',55),
('9-11','Capítulo','Salmos 145',105)
]

# Connect to the database
try:
    connection = psycopg2.connect(DATABASE_URL)
    cursor = connection.cursor()

    # Insert the data into the correct table - 'citas'
    insert_query = """
    INSERT INTO citas (clase, tipo, cita, puntaje)
    VALUES (%s, %s, %s, %s)
    """
    cursor.executemany(insert_query, data)

    # Commit the transaction to save data
    connection.commit()
    print(f"Successfully inserted {len(data)} rows into the 'citas' table.")

except Exception as error:
    print(f"An error has occurred: {error}")

finally:
    # Clean up by closing the database cursor and connection
    if cursor:
        cursor.close()
    if connection:
        connection.close()