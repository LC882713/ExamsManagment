from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table, Column, Integer, String, MetaData
from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.orm import sessionmaker


url='postgresql://postgres:admin@localhost:5432/ProgettoBasiDati23'
#url='postgresql://postgres:postgres@localhost:5432/ProgettoBasi'

if not database_exists(url):
    create_database(url)

engine = create_engine(url, echo=True)
metadata=MetaData()

Base=declarative_base()


class Users(Base):
   __tablename__='users'
   id=Column(Integer, primary_key=true, autoincrement=True)
   name=Column(String, nullable=false)
   surname=Column(String, nullable=false)
   email=Column(String, nullable=false)
   password=Column(String, nullable=false)
   gender=Column(String, nullable=false)
   role=Column(String, nullable=false)

class Exams(Base):
   __tablename__='exams'
   id_exam=Column(Integer, primary_key=true, autoincrement=True)
   name=Column(String, nullable=false)
   credits=Column(Integer, nullable=false)
   num_tests=Column(Integer, nullable=false)
   id_professors= Column(Integer, ForeignKey(Users.id), nullable=false)

class Tests(Base):
   __tablename__='tests'
   id_test=Column(Integer, primary_key=true,autoincrement=True)
   name=Column(String, nullable=false)
   type=Column(String, nullable=false)
   bonus=Column(Integer, nullable=false) 
   grade_weight=Column(Integer, nullable=false) 
   id_exams=Column(Integer, ForeignKey(Exams.id_exam), nullable=false)

class Sessions(Base):
   __tablename__='sessions'
   id_session=Column(Integer, primary_key=true, autoincrement=True)

class Sessions_tests(Base):
   __tablename__='sessions_tests'
   id_sessions=Column(Integer, ForeignKey('sessions.id_session'), primary_key=True)
   id_tests= Column(Integer, ForeignKey('tests.id_test'), primary_key=True)
   date=Column(DATE) 
   __table_args__ = (
        PrimaryKeyConstraint('id_sessions', 'id_tests'),
    )

class Registrations(Base):
   __tablename__='registrations'
   id_registrations=Column(Integer, primary_key=true, autoincrement=True)
   verb_date=Column(DATE) 
   expiration_date=Column(DATE) 
   grade=Column(Integer)
   register=Column(String)   
   id_students=Column(Integer, ForeignKey(Users.id))
   id_tests=Column(Integer, ForeignKey(Tests.id_test))
   id_sessions=Column(Integer, ForeignKey(Sessions.id_session))

class Professors_tests(Base):
   __tablename__='professors_tests'
   id_professors = Column(Integer, ForeignKey('users.id'), primary_key=True)
   id_tests = Column(Integer, ForeignKey('tests.id_test'), primary_key=True)
   __table_args__ = (
        PrimaryKeyConstraint('id_professors', 'id_tests'),
    )
class Students_exams(Base):
   __tablename__='students_exams'
   id_students = Column(Integer, ForeignKey('users.id'), primary_key=True)
   id_exams = Column(Integer, ForeignKey('exams.id_exam'), primary_key=True)
   total_grade= Column(Integer , nullable=false)
   __table_args__ = (
        PrimaryKeyConstraint('id_students', 'id_exams'),
    )

Base.metadata.create_all(engine)
conn=engine.connect()   

def create_roles():
   try:
      conn.execute(text(open("roles.sql").read()))
      print("ruoli creati")
   except Exception as e:
      print( f"errore creazione ruoli:{e}")
      
create_roles()

def create_trigger():
   try:
      with engine.connect() as conn:
         conn.execute(text(open("triggers.sql").read()))
      print("triggers creati")
   except Exception as e:
      print (f"errore creazione trigger:{e}")


create_trigger()

def populate():
   try:
      # Create a session
      Session = sessionmaker(bind=engine)
      session = Session()
      # Controlla se la tabella users è vuota
      user_count = session.query(Users).count()

      if user_count == 0:
         sql_commands = None  
         with open("populate.sql") as file:
            sql_commands = file.read()
      
         if sql_commands is not None:
            # Commit the SQL commands using the session
            session.execute(text(sql_commands))
            session.commit()
            print("Popolamento completato con successo.")
         else:
            print("Il file populate.sql è vuoto.")
            
      else:
         print("La tabella users non è vuota. Non è necessario popolare.")

      # Close the session after the population process
      session.close()

   except Exception as e:
        print(f"Errore durante il popolamento: {e}")
   
populate()


