#Please Install using pip3 install SQLALCHEMY
#This cell creates required tables
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column, Date, Integer, String, and_, not_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref, sessionmaker
from datetime import datetime, timedelta
import json

engine = create_engine('sqlite:///lib.db', echo=False)#Set this to true if SQLALchemy logs are to be enabled
Base = declarative_base()
Session = sessionmaker(bind = engine)
session = Session()

class StudentModel(Base):
    #create table Students
    __tablename__='students'

    student_id=Column(Integer, primary_key=True)
    std_name=Column(Integer)
    std_surname=Column(String(80))
    borrowed_amt=Column(Integer)
    borrow=relationship('BorrowModel')
    
    #Initialisation Method
    
    def __init__(self, std_name,std_surname,borrowed_amt):
        self.std_name=std_name
        self.std_surname=std_surname
        self.borrowed_amt=borrowed_amt

    @classmethod
    def find_by_name(cls,std_name):
        return session.query(cls).filter(cls.std_name.like('%'+std_name+'%'))

        
    @classmethod
    def check_limit(cls,student_id):
        return cls.query.filter_by(student_id=student_id)
    

class BookModel(Base):
    #create Books table
    __tablename__="books"

    
    book_id=Column(Integer, primary_key=True)
    isbn=Column(String(10))
    bk_title=Column(String(80))
    bk_subject=Column(String(100))
    bk_author=Column(String(30))
    bk_quantity=Column(Integer)
    borrow=relationship('BorrowModel')

    #Initialisation Method
   
    def __init__(self, isbn, book_title,subject,authors,quantity):
        self.isbn=isbn
        self.bk_title=book_title
        self.bk_author=authors
        self.bk_subject=subject
        self.bk_quantity=quantity

    @classmethod
    def find_by_isbn(cls,isbn):
        return session.query(cls).filter(cls.isbn.like('%'+isbn+'%')).all()

    @classmethod
    def find_by_title(cls,bk_title):
        return session.query(cls).filter(cls.bk_title.like('%'+bk_title+'%')).all()
    
    @classmethod
    def find_by_subject(cls,bk_subject):
        return session.query(cls).filter(cls.bk_subject.like('%'+bk_subject+'%')).all()
    
    @classmethod
    def find_by_author(cls,bk_author):
        return session.query(cls).filter(cls.bk_author.like('%'+bk_author+'%')).all()
        
    
class BorrowModel(Base):
    #create Borrow Table
    __tablename__='borrows'

    borrow_id=Column(Integer, primary_key=True)
    student_id=Column(Integer,ForeignKey('students.student_id'))
    book_id=Column(String(80),ForeignKey('books.book_id'))
    borrowed_date=Column(Date)
    available_date=Column(Date)
    status=Column(String(30))
    borrow=relationship(StudentModel)
    book=relationship(BookModel)

    #Initialisation Method
    def __init__(self,student_id,book_id,status):
        self.student_id=student_id
        self.book_id=book_id
        self.status=status
        self.borrowed_date=datetime.now()
        self.available_date=datetime.now() + timedelta(days=7)
        
#This code creates all tables in lib.db        
Base.metadata.create_all(engine)

def check_books(std_id):
    '''This cell checks students borrow quota. 
        First checks the quota, 
        if doesn't exceed then 
        it will be incremented every time a book
        is allocated'''
    rows=session.query(StudentModel).filter(StudentModel.student_id==std_id)
    items=[]
    for row in rows:
        item={
            "id":row.student_id,
            "name":row.std_name,
            "surname":row.std_surname,
            "borrowed books": row.borrowed_amt
        }
        items.append(item)

        if(row.borrowed_amt<2):
            return True
        else:
            return False
            


'''This section allows user to borrow book
Note the entries in Borrows table automatically populates, also the next available date
The book can currently be borrowed using ISBN of the book'''
def check_availability(bookISBN,std_id):
    item=[]
    rw=session.query(BookModel).filter(and_(BookModel.isbn==bookISBN,BookModel.bk_quantity!=0)).one_or_none()
    if rw:
        item={
            "Book_ID":rw.book_id,
            "ISBN":rw.isbn,
            "Book title":rw.bk_title,
            "Book Author": rw.bk_author,
            "Book Subject":rw.bk_subject,
            "Quantity":rw.bk_quantity}

        if check_books(std_id) is True:
            return bookborrow(std_id,rw.book_id)
        else:
            return "You have already borrowed two books!"

        
    else:
        rows=session.query(BorrowModel).join(BookModel).filter(BookModel.isbn==bookISBN)
        items=[]
        for row in rows:
            item={"Available Date":row.available_date}
            items.append(item)
        if items:
            return "Book Not available, it will be available on {}".format(items[0]['Available Date'])

        return "Book Not available, we can't give a date as when this will be available"
    
def bookborrow(std_id,book_id):
    #updates students borrow_amt column by 1
    try:
        session.query(StudentModel).filter(StudentModel.student_id==std_id).update({StudentModel.borrowed_amt: StudentModel.borrowed_amt+1})
        session.commit()
    except:
        return "Error occured while updating borrow amount"
    
    #updates book availability
    try:
        session.query(BookModel).filter(BookModel.book_id==book_id).\
        update({BookModel.bk_quantity: BookModel.bk_quantity-1})
        session.commit()
    except:
        "Error updating book availability"

    try:
        borrow1=BorrowModel(std_id,book_id,"Issued")
        session.add(borrow1)
        session.commit()
    except:
        return "Error occured while upadting borrow table"
    return "Book successfully borrowed for 7 days"


'''This section allows students to return the books, note the change in tables'''
def bookcheck(std_id):
    #This query joins BorrowModel and StudentModel on student_id.
    #Its used to filter student and check the status.
    rows=session.query(BorrowModel).join(StudentModel)\
    .filter(and_(StudentModel.borrowed_amt!=0,BorrowModel.student_id==std_id,\
                 not_(BorrowModel.status.contains('Returned'))))
    return rows
            
def bookreturn(std_id,bk_id):
    items=[]
    rows=session.query(BorrowModel).filter(and_(BorrowModel.book_id==bk_id,\
        BorrowModel.student_id==std_id,not_(BorrowModel.status.contains('Returned'))))
    for row in rows:
        items.append(row)

    if len(items)!=0:
        session.query(BorrowModel).filter(and_(BorrowModel.book_id==bk_id,BorrowModel.student_id==std_id)).\
        update({BorrowModel.status:"Returned"})

        session.query(BookModel).filter(BookModel.book_id==bk_id).\
        update({BookModel.bk_quantity: BookModel.bk_quantity+1})
            
        session.query(StudentModel).filter(StudentModel.student_id==std_id).\
         update({StudentModel.borrowed_amt: StudentModel.borrowed_amt-1})
        session.commit()
    
        return "Book Successfully returned"
    else:
        return "Please check book ID and Student ID you have entered"



# if bookcheck(std_id)!=0:
#     print(items)
#     bk_id=str(input("Enter the Book_ID from the list: "))
#     for i in items:
#         if i['Book ID']==bk_id:
#             bookreturn(std_id,int(bk_id))
#         else:
#             return "No such book is allocated"
    
# else:
#     return "Student ID doesn't exist OR you might not have borrowed that book"