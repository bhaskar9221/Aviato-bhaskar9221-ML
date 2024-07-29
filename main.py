from fastapi import FastAPI, HTTPException, Path
from pydantic import BaseModel
from google.cloud import firestore
import os
from typing import Dict, Any
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
from dotenv import load_dotenv

from email_validator import validate_email, EmailNotValidError
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


# Set the path to your service account key file
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "aviato-api-bhaskar9221-4869a5d3010d.json"

# Initialize Firestore DB with explicit project ID
db = firestore.Client(project='aviato-api-bhaskar9221')

class User(BaseModel):
    username: str
    email: str
    project_id: str

    class Config:
        extra = 'allow'

app = FastAPI()





# Email configuration from environment variables
SMTP_SERVER = os.getenv('SMTP_SERVER')
SMTP_PORT = int(os.getenv('SMTP_PORT'))
SMTP_USER = os.getenv('SMTP_USER')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')

class EmailRequest(BaseModel):
    subject: str

@app.post("/send_invitation")
async def send_invitation(email_request: EmailRequest):
    try:
        recipients = [
            "bhaskarmondal7221@gmail.com",
            
        ]
        
        with open("email_template.html", "r") as file:
            email_body = file.read()

        msg = MIMEMultipart()
        msg['From'] = formataddr(('Your Name', SMTP_USER))
        msg['To'] = ', '.join(recipients)
        msg['Subject'] = email_request.subject
        msg.attach(MIMEText(email_body, 'html'))

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(msg)

        return {"message": "Invitation emails sent successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 





@app.get("/users")
async def get_users():
    try:
        users_ref = db.collection('user')
        docs = users_ref.stream()
        users = []
        for doc in docs:
            user_data = doc.to_dict()
            user_data['id'] = doc.id
            users.append(user_data)
        return users
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/add_users")
async def create_user(user: User):
    try:
        users_ref = db.collection('user')
        # Use add() to auto-generate a document ID
        doc_ref = users_ref.add(user.model_dump())
        
        doc_data = user.model_dump()
        return {"message": "User created successfully", "user": doc_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.patch("/update_users/{user_id}")
async def update_user(user_id: str, update_fields: Dict[str, Any]):
    try:
        users_ref = db.collection('user').document(user_id)
        if not users_ref.get().exists:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Update the document with new data
        users_ref.update(update_fields)
        
        # Retrieve updated data
        updated_doc = users_ref.get()
        updated_data = updated_doc.to_dict()
        updated_data['id'] = user_id
        return {"message": "User updated successfully", "user": updated_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/delete_users/{user_id}")
async def delete_user(user_id: str):
    try:
        users_ref = db.collection('user').document(user_id)
        if not users_ref.get().exists:
            raise HTTPException(status_code=404, detail="User not found")
        # Delete the document
        users_ref.delete()
        return {"message": "User deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Run the application using uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
