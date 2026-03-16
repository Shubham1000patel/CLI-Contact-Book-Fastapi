# FastAPI Multi-Feature Application

A FastAPI application that provides contact management, salary prediction using machine learning, and image classification for fashion items using a deep learning vision model.

## Features

- **Contact Management**: Add, list, update, and delete contacts stored in a local SQLite database.
- **Salary Prediction**: Predict employee salaries based on department using a trained machine learning model.
- **Vision Classification**: Classify fashion items from uploaded images using a PyTorch-based neural network trained on FashionMNIST.

## Installation

1. Clone or download the repository.

2. Install the required dependencies:

   ```bash
   pip install fastapi uvicorn pydantic joblib torch torchvision pillow
   ```

   Note: Ensure you have the model files (`salary_model.pkl`, `vision_weights.pth`) and the `vision_model.py` file in the project directory.

## Running the Application

1. Start the server:

   ```bash
   uvicorn main:app --reload
   ```

2. Open the interactive API documentation:

   - Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
   - ReDoc: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

## Endpoints

### Contact Management

#### GET /contacts
Retrieve all contacts from the database.

**Response**:
```json
{
  "status": "success",
  "data": [
    {"name": "John Doe", "phone": "123-456-7890"}
  ]
}
```

#### POST /add_contact
Add a new contact.

**Request Body**:
```json
{
  "name": "Jane Doe",
  "phone": "987-654-3210"
}
```

**Response**:
```json
{
  "status": "success",
  "message": "Contact 'Jane Doe' added to database."
}
```

#### PUT /update_contact/{name}
Update an existing contact's phone number.

**Request Body**:
```json
{
  "new_phone": "555-123-4567"
}
```

**Response**:
```json
{
  "status": "success",
  "message": "Contact 'John Doe' updated with new phone number."
}
```

#### DELETE /delete_contact/{name}
Delete a contact by name.

**Response**:
```json
{
  "status": "success",
  "message": "Contact 'Jane Doe' deleted."
}
```

### Salary Prediction

#### POST /predict_salary
Predict the salary for an employee based on department.

**Request Body**:
```json
{
  "department": "IT"
}
```

**Response**:
```json
{
  "department": "IT",
  "predicted_salary_inr": 65000.0
}
```

*Note*: Department must be one of "HR", "IT", or "Sales".

### Vision Classification

#### POST /predict_vision
Classify a fashion item from an uploaded image.

**Request**: Multipart form data with an image file.

**Response**:
```json
{
  "prediction": "T-shirt/top"
}
```

*Note*: The model expects grayscale images and resizes them to 28x28 pixels. Supported classes: T-shirt/top, Trouser, Pullover, Dress, Coat, Sandal, Shirt, Sneaker, Bag, Ankle boot.

## Database

The application uses a local SQLite database (`contact_master.db`) for storing contacts. The database is initialized automatically on startup.

## Models

- **Salary Model**: A machine learning model loaded from `salary_model.pkl`.
- **Vision Model**: A PyTorch neural network loaded from `vision_weights.pth`, defined in `vision_model.py`.

Ensure all model files are present in the project directory before running the application.

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
