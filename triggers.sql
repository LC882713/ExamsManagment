--trigger che controlla che la data inserita non sia di sabato o domenica
--funzione EXTRACT con l'opzione ISODOW per ottenere il giorno della settimana in formato ISO (1 per lunedì, 2 per martedì, ..., 7 per domenica).
--Se il giorno della settimana è 6 (sabato) o 7 (domenica), viene generata un'eccezione che impedisce l'inserimento dell'evento.
CREATE OR REPLACE FUNCTION check_date_weekend() RETURNS TRIGGER AS $$
BEGIN
  IF EXTRACT(ISODOW FROM NEW.date) IN (6,7) THEN
    RAISE EXCEPTION 'Il test non può essere fatto nei weekend';
  END IF;
  RETURN NEW;
END;
$$LANGUAGE plpgsql;


DROP TRIGGER IF EXISTS no_weekend ON sessions_tests;
CREATE TRIGGER no_weekend
BEFORE INSERT OR UPDATE ON sessions_tests
FOR EACH ROW
EXECUTE FUNCTION check_date_weekend();






---trigger che controlla che tutti i voti dei test di un esame siano sufficienti prima di registrare il voto finale
CREATE OR REPLACE FUNCTION check_exam_passed() RETURNS TRIGGER AS $$
BEGIN
  IF EXISTS (
    SELECT registrations.grade
    FROM registrations
    JOIN tests ON registrations.id_tests = tests.id_test
    JOIN exams ON exams.id_exam = tests.id_exams
    WHERE registrations.grade < 18
  ) THEN
    RAISE EXCEPTION 'Impossibile inserire o aggiornare l''esame';
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;


DROP TRIGGER IF EXISTS final_grade ON students_exams;
CREATE TRIGGER final_grade
BEFORE INSERT OR UPDATE ON exams
FOR EACH ROW
EXECUTE FUNCTION check_exam_passed();




---trigger che controlla che un test non sia scaduto quando si va ad inserire il voto totale di un esame
CREATE OR REPLACE FUNCTION check_date_expiration() RETURNS TRIGGER AS $$
BEGIN
    IF EXISTS(
      SELECT registrations.expiration_date
      FROM registrations
      JOIN tests ON registrations.id_tests = tests.id_test
      JOIN exams ON exams.id_exam = tests.id_exams
      WHERE registrations.expiration_date <CURRENT_DATE
    )THEN
      RAISE NOTICE 'La prova è scaduta, non può quindi essere utilizzata per il voto totale';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


DROP TRIGGER IF EXISTS expiration_date_trigger ON students_exams;
CREATE TRIGGER expiration_date_trigger
BEFORE INSERT OR UPDATE
ON exams
FOR EACH ROW
EXECUTE FUNCTION check_date_expiration();










--trigger che controlla che la somma dei pesi dei vari test sia 100
CREATE OR REPLACE FUNCTION grade_weight() RETURNS TRIGGER AS $$
DECLARE
numtestrequired INTEGER;
total INTEGER;
numtest INTEGER;
BEGIN
--estrae il numero dei test previsto dalla tabella esami
  SELECT exams.num_tests
  INTO numtestrequired
  FROM exams
  WHERE exams.id_exam= NEW.id_exams;

--calcola il numero dei test attualmente inseriti per l'esame corrente
  SELECT COUNT (*)
  INTO numtest
  FROM tests
  WHERE id_exams=NEW.id_exams;

--calcola la somma dei grade_weight se il numero dei test inseriti corrisponde al nuemro dei test della tabella esami
  IF numtestrequired=numtest THEN
    SELECT SUM(grade_weight)
    INTO total
    FROM tests
    WHERE id_exams=NEW.id_exams;
    IF total != 100
    THEN RAISE EXCEPTION 'Il totale del peso dei voti non corrisponde a 100';
    END IF;
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS control_grade_weight ON tests;
CREATE TRIGGER control_grade_weight
AFTER INSERT OR UPDATE ON tests
FOR EACH ROW
EXECUTE FUNCTION grade_weight();




--non possono essere creati due esami uguali
CREATE  OR REPLACE FUNCTION double_exam() RETURNS TRIGGER AS $$
BEGIN
  IF EXISTS (SELECT * FROM exams WHERE name=NEW.name)
  THEN RAISE NOTICE 'impossibile creare un altro esame con lo stesso nome';
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;


CREATE TRIGGER no_double_exam
BEFORE INSERT OR UPDATE ON exams
FOR EACH ROW
EXECUTE FUNCTION double_exam();




--trigger che controlla che prima di aver fatto un progetto bisogna aver fatto lo scritto
CREATE OR REPLACE FUNCTION written_before_project() RETURNS TRIGGER AS $$
BEGIN
  IF EXISTS (
    SELECT 1
    FROM exams e1
    JOIN tests t1 ON e1.id_exam = t1.id_exams JOIN registrations r ON t1.id_test = r.id_tests
    WHERE t1.type = 'project'
    AND NOT EXISTS (
        SELECT *
        FROM exams e2
        JOIN tests t2 ON e2.id_exam = t2.id_exams JOIN registrations r2 ON t2.id_test = r2.id_tests
        WHERE t2.type = 'written'
        AND e2.id_exam = e1.id_exam AND r2.grade IS NOT NULL
    )
    )
    THEN
    RAISE EXCEPTION 'Prima di discutere il progetto bisogna aver superato lo scritto';
  END IF;
  RETURN NEW;
  END;
  $$LANGUAGE plpgsql;


CREATE TRIGGER no_written_no_project
AFTER UPDATE ON registrations
FOR EACH ROW
EXECUTE FUNCTION  written_before_project();




--trigger invalidazione
CREATE FUNCTION invalidation_exam() RETURNS TRIGGER AS $$
BEGIN
--controlla se esiste un test con lo stesso nome del test che sto inserendo e dello stesso studente
--e che abbia una data di svolgimento precedente rispetto a quella a cui mi sto iscrivendo (mi sto iscrivendo
--ad un test che ho già fatto in precedenza)
  IF EXISTS (
    SELECT r.id_registrations
    FROM registrations r J
    WHERE r.id_students=NEW.id_students AND r.id_tests=NEW.id_tests AND r.verb_date< NEW.verb_date)
    THEN
    DELETE FROM registrations
    WHERE id_students=NEW.id_students AND id_tests=NEW.id_tests AND verb_date< NEW.verb_date;
  END IF;
  RETURN NEW;
END;
$$LANGUAGE plpgsql;


CREATE TRIGGER invalidation
AFTER INSERT OR UPDATE ON registrations
FOR EACH ROW
EXECUTE FUNCTION invalidation_exam();



