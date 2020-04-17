from flask import Flask, request
from flask import render_template
from tabels import BookModel, BookModel, StudentModel
import tabels

app=Flask(__name__)

@app.route('/',methods=['GET','POST'])
def home():
    return render_template('home.html')

@app.route('/search')
def searchpage():
    return render_template('search.html')
    
@app.route('/books/author',methods=['POST'])
def author_search():
    data=request.form
    rows=BookModel.find_by_author(data['Name'])
    items=[]
    #prints the selected rows
    for row in rows:
        item={
            "Book_ID":row.book_id,
            "ISBN":row.isbn,
            "Book title":row.bk_title,
            "Book Author": row.bk_author,
            "Book Subject":row.bk_subject,
            "Quantity":row.bk_quantity
            
        }
        items.append(item)
    return render_template('booksearch.html',items=items, len=len(items))

@app.route('/books/title',methods=['POST'])
def title_search():
    data=request.form
    rows=BookModel.find_by_title(data['Name'])
    items=[]
    #prints the selected rows
    for row in rows:
        item={
            "Book_ID":row.book_id,
            "ISBN":row.isbn,
            "Book title":row.bk_title,
            "Book Author": row.bk_author,
            "Book Subject":row.bk_subject,
            "Quantity":row.bk_quantity
            
        }
        items.append(item)
    return render_template('booksearch.html',items=items, len=len(items))

@app.route('/books/isbn',methods=['POST'])
def isbn_search():
    data=request.form
    rows=BookModel.find_by_isbn(data['Name'])
    items=[]
    #prints the selected rows
    for row in rows:
        item={
            "Book_ID":row.book_id,
            "ISBN":row.isbn,
            "Book title":row.bk_title,
            "Book Author": row.bk_author,
            "Book Subject":row.bk_subject,
            "Quantity":row.bk_quantity
            
        }
        items.append(item)
    return render_template('booksearch.html',items=items, len=len(items))
@app.route('/borrowbook')
def borrowpage():
    return render_template('borrow.html')

@app.route('/borrow',methods=['POST'])
def borrowbook():
    data=request.form
    return tabels.check_availability(data['isbn'],data['student_id'])

@app.route('/checkreturn')
def checkreturnpage():
    return render_template('checkbookreturn.html')

@app.route('/bookcheck',methods=['POST'])
def book_id_check_by_students():
    data=request.form
    rows=tabels.bookcheck(data['std_id'])
    items=[]
    if rows:
        for row in rows:
            item={
        "Student ID":row.student_id,
        "Book ID":row.book_id,
        "Borrowed Date":row.borrowed_date,
        "Due Date":row.available_date,
        "Status":row.status}
            items.append(item)
        if len(items)!=0:
            return render_template('bookreturn.html',items=items, len=len(items))
        return "No such student exist"

@app.route('/return')
def returnpage():
    return render_template('return.html')

@app.route('/bookreturn',methods=['POST'])
def return_book():
    data=request.form
    return tabels.bookreturn(data['std_id'],data['bk_id'])


app.run(debug=True)