import csv
from application import db

# same import and setup statements as above
f = open("books.csv")
reader = csv.reader(f)
for isbn, title, author, year in reader: # loop gives each column a name
    db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)",
            {"isbn": isbn, "title": title, "author": author, "year": int(year)}) # substitute values from CSV line into SQL command, as per this dict
db.commit() # transactions are assumed, so close the transaction finished
