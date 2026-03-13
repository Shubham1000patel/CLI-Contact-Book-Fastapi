# FastAPI Contact Manager

A small FastAPI app that manages a simple contact list stored in a local SQLite database (`contact_master.db`).

## ✅ Features

- Add a contact (`POST /add_contact`)
- List all contacts (`GET /contacts`)
- Update a contact's phone number (`PUT /update_contact/{name}`)
- Delete a contact (`DELETE /delete_contact/{name}`)

## ▶️ Run the App

1. Install dependencies:

```bash
pip install fastapi uvicorn pydantic
```

2. Start the server:

```bash
uvicorn main:app --reload
```

3. Open the interactive API docs:

- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

## 🧩 Endpoints

### GET /contacts
Return all contacts in the database.

### POST /add_contact
Create a new contact.

**Request body** (JSON):

```json
{
  "name": "Jane Doe",
  "phone": "123-456-7890"
}
```

### PUT /update_contact/{name}
Update an existing contact's phone number.

**Request body** (JSON):

```json
{
  "new_phone": "987-654-3210"
}
```

### DELETE /delete_contact/{name}
Delete an existing contact by name.

## 📝 Notes

- The app stores data in a local SQLite database file named `contact_master.db` in the project directory.
- Names are normalized (trimmed + title-cased) before being stored/queried.
