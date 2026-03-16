from torchvision import transforms
from vision_model import VisionBrain # Imports the blueprint from your other file
from PIL import ImageOps
import joblib
from fastapi import FastAPI
from pydantic import BaseModel
import sqlite3
from fastapi import FastAPI, HTTPException
from fastapi import File, UploadFile
from PIL import Image
import io
import torch


app = FastAPI()




print("Loading Custom Salary Model...")
salary_model = joblib.load("salary_model.pkl")
print("Salary Model Loaded Successfully!")

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

class EmployeeData(BaseModel):
    department: str # Expecting "HR", "IT", or "Sales"    
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
    
@app.post("/predict_salary")
def predict_salary(data: EmployeeData):
    # 1. Standardize the input (handle lowercase/uppercase variations)
    dept = data.department.upper()
    
    # 2. The Translation Layer (String -> One-Hot Encoded Matrix)
    # The model strictly expects: [HR, IT, Sales]
    if dept == "HR":
        features = [[1, 0, 0]]
    elif dept == "IT":
        features = [[0, 1, 0]]
    elif dept == "SALES":
        features = [[0, 0, 1]]
    else:
        # If the user sends "Marketing", the model will crash because it wasn't trained on it.
        # We must block invalid data before it hits the AI.
        raise HTTPException(status_code=400, detail="Department must be HR, IT, or Sales")

    # 3. Feed the matrix into the serialized ML model
    prediction = salary_model.predict(features)
    
    # 4. Clean up the output (prediction looks like [52500.0])
    final_salary = round(prediction[0], 2)
    
    # 5. Return the response
    return {
        "department": dept,
        "predicted_salary_inr": final_salary
    }   
    # --- DEEP LEARNING VISION SETUP ---
print("Loading Deep Learning Vision Model...")

# 1. Build the empty brain
vision_model = VisionBrain()

# 2. Pour the learned weights into the brain
vision_model.load_state_dict(torch.load("vision_weights.pth"))

# 3. Lock the brain (Evaluation Mode - Critical for production)
vision_model.eval()
print("Vision Model Loaded Successfully!")

# 4. The Image Translation Layer
# This forces any uploaded image to become a 28x28 grayscale Tensor
vision_transform = transforms.Compose([
    transforms.Grayscale(num_output_channels=1),
    transforms.Resize((28, 28)),
    transforms.ToTensor()
])

fashion_dictionary = [
    "T-shirt/top", "Trouser", "Pullover", "Dress", "Coat",
    "Sandal", "Shirt", "Sneaker", "Bag", "Ankle boot"
]


@app.post("/predict_vision")
async def predict_vision(file: UploadFile = File(...)):
    # 1. Read the physical image file sent by the user
    image_bytes = await file.read()
    image = Image.open(io.BytesIO(image_bytes))

    # --- THE INVERSION FIX ---
    # Convert the image to pure grayscale first
    image = image.convert("L")
    # Invert the colors (White background becomes Black, Dark shirt becomes Light!)
    image = ImageOps.invert(image)
    
    # 2. Translate the image into a mathematical Tensor
    # .unsqueeze(0) adds a fake "batch" dimension so the shape becomes [1, 1, 28, 28]
    input_tensor = vision_transform(image).unsqueeze(0)
    
    # 3. Feed the Tensor to the AI
    with torch.no_grad():
        prediction_logits = vision_model(input_tensor)
        predicted_index = prediction_logits.argmax(1).item()
        
    # 4. Translate the math back to English
    predicted_clothing = fashion_dictionary[predicted_index]
    
    return {
        "filename": file.filename,
        "ai_prediction": predicted_clothing,
        "confidence_note": "Model trained to 83.7% accuracy"
    }