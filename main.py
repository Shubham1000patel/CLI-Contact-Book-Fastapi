from fastapi import FastAPI
from pydantic import BaseModel
import sqlite3
from fastapi import FastAPI, HTTPException

app = FastAPI()

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import sqlite3

app = FastAPI()

# --- ADD THIS NEW BLOCK ---
def init_db():
    conn = sqlite3.connect("contact_master.db")
    cursor = conn.cursor()
    # Create the table ONLY if it doesn't already exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contacts (
            name TEXT,
            number TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Run the setup function immediately when the server boots
init_db()

# 1. Define the "Shape" of the incoming data using Pydantic
# This tells FastAPI: "Only accept requests that look exactly like this."

class NewContact(BaseModel):
    name: str
    phone: str

class UpdateContact(BaseModel):    
    
    new_phone: str
@app.get("/contacts")
def get_all_ccontacts():

    conn = sqlite3.connect("contact_master.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM contacts")
    records = cursor.fetchall()
    conn.close()



    contact_list = []
    for row in records:
        contact_list.append({"name": row[0], "phone": row[1]})



    return {"status": "success", "data": contact_list}    


@app.post("/add_contact",status_code=201)
def create_contact(contact: NewContact): # FastAPI automatically converts the JSON into this object
    
    conn = sqlite3.connect("contact_master.db")
    cursor = conn.cursor()
    
    # 3. Clean the data immediately! (Fixing your "Shubham " bug)
    clean_name = contact.name.strip().title()
    clean_phone = contact.phone.strip() 


    # 4. Insert into database
    cursor.execute("INSERT INTO contacts (name, number) VALUES (?, ?)", (clean_name, clean_phone))
    conn.commit()
    conn.close()
    
    # 5. Return a success response
    return {"status": "success", "message": f"Contact '{clean_name}' added to database."}  

# 1. We put {name} in the URL route. This is the Path Parameter.
@app.delete("/delete_contact/{name}")
def delete_contact(name: str): # 2. FastAPI automatically pulls the name from the URL into this variable!
    
    conn = sqlite3.connect("contact_master.db")
    cursor = conn.cursor()
    
    # 3. Clean the input (always!)
    clean_name = name.strip().title()
    
    # 4. Execute the DELETE query
    cursor.execute("DELETE FROM contacts WHERE name = ?", (clean_name,))
    
    # 5. Check rowcount just like we did in the CLI version!
    if cursor.rowcount == 0:
        conn.close()
        # This will immediately stop the function and send a 404 Error to the client
        raise HTTPException(status_code=404, detail=f"Contact '{clean_name}' not found.")
    else:
        conn.commit()
        conn.close()
        return {"status": "success", "message": f"Contact '{clean_name}' deleted."} 

@app.put("/update_contact/{name}")  # FIXED: Now it is a PUT request
def update_contact(name: str, update: UpdateContact):
    conn = sqlite3.connect("contact_master.db")
    cursor = conn.cursor()
    
    clean_name = name.strip().title() # FIXED: Standardize the name format
    clean_new_phone = update.new_phone.strip()
    
    # FIXED: Two question marks, two variables in the tuple
    cursor.execute("UPDATE contacts SET number = ? WHERE name = ?", (clean_new_phone, clean_name))
    
    if cursor.rowcount == 0:
        conn.close()
        # This will immediately stop the function and send a 404 Error to the client
        raise HTTPException(status_code=404, detail=f"Contact '{clean_name}' not found.")
    else:
        conn.commit()
        conn.close()
        return {"status": "success", "message": f"Contact '{clean_name}' updated with new phone number."}