# School Management System ERD

This document provides instructions for using the Entity Relationship Diagram (ERD) created for the School Management System.

## Using the ERD with dbdiagram.io

The ERD has been created in DBML (Database Markup Language) format for use with [dbdiagram.io](https://dbdiagram.io/).

### Steps to View the ERD

1. Open your web browser and go to [dbdiagram.io](https://dbdiagram.io/)
2. If you don't have an account, you can use the site without logging in
3. Click on "Import" in the top right corner
4. Select "Import from DBML"
5. Open the file `school_erd.dbml` in a text editor
6. Copy all the content from the file
7. Paste it into the import text area in dbdiagram.io
8. Click "Import"

The diagram will be rendered showing all entities and their relationships.

## Understanding the ERD

The ERD includes the following main entities:

- **School**: Represents educational institutions in the system
- **User**: Represents all users (admins, teachers, students, parents)
- **Role**: Defines the different roles users can have
- **Subject**: Represents academic subjects taught in schools
- **Schedule/ScheduleItem**: Represents timetables and individual scheduled classes
- **Assignment/AssignmentSubmission**: Represents homework assignments and student submissions
- **Test**: Represents exams and quizzes
- **Grade**: Represents assessment scores for assignments and tests
- **Attendance**: Tracks student attendance in classes

## Association Tables

Several many-to-many relationships are represented by association tables:

- **user_roles**: Links users to their roles
- **parent_student**: Links parent users to their children (student users)
- **teacher_subject**: Links teachers to the subjects they teach
- **subject_enrollment**: Links students to subjects they are enrolled in

## Customizing the ERD

You can customize the ERD in dbdiagram.io by:

1. Changing the colors and styles of entities
2. Rearranging the layout for better visualization
3. Adding notes or additional information
4. Exporting to different formats (PNG, PDF, SQL, etc.)

## Generating SQL from the ERD

dbdiagram.io allows you to generate SQL for different database systems:

1. Click on "Export" in the top right corner
2. Select "Export to SQL"
3. Choose your database system (PostgreSQL, MySQL, SQL Server, etc.)
4. Copy the generated SQL or download it as a file

This SQL can be used to create the database schema in your chosen database system.

## Additional Notes

- The ERD shows both table structures and relationships
- Foreign key constraints are represented by arrows between tables
- Association tables handle many-to-many relationships
- Nullable fields are marked appropriately

For any questions or modifications needed to the ERD, please update the `school_erd.dbml` file and re-import it into dbdiagram.io.