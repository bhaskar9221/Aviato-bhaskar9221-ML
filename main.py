from fastapi import FastAPI, HTTPException, Path
from pydantic import BaseModel, EmailStr
from google.cloud import firestore
import os
from typing import Dict, Any
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
from dotenv import load_dotenv

from email_validator import validate_email, EmailNotValidError

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






def send_email(to_email: str, subject: str, message: str):
    
    
    
    # Replace these with your email server details
    smtp_server = os.getenv('SMTP_SERVER')
    smtp_port = int(os.getenv('SMTP_PORT', 587))
    smtp_username = os.getenv('SMTP_USER')
    smtp_password = os.getenv('SMTP_PASSWORD')

    msg = MIMEMultipart("alternative")
    msg['From'] = smtp_username
    msg['To'] = to_email
    msg['Subject'] = subject

    # HTML content with placeholders for dynamic data
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            .container {{
                width: 100%;
                background-color: #f9f9f9;
                padding: 20px;
                font-family: Arial, sans-serif;
            }}
            .header {{
                background-color: #007bff;
                color: white;
                padding: 10px;
                text-align: center;
                font-size: 24px;
                font-weight: bold;
            }}
            .content {{
                padding: 20px;
                background-color: white;
                margin: 20px auto;
                width: 80%;
                border-radius: 10px;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            }}
            .button {{
                background-color: #007bff;
                color: white;
                padding: 10px 20px;
                text-align: center;
                text-decoration: none;
                display: inline-block;
                margin: 20px 0;
                border-radius: 5px;
            }}
            .footer {{
                background-color: #007bff;
                color: white;
                padding: 10px;
                text-align: center;
                font-size: 14px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">API Documentation Invitation</div>
            <div class="content">
                <p>Hello,</p>
                <p>I am are excited to invite you to view my User Management API documentation on <b>ReDoc</b>.</p>
                <p>You can access the documentation by clicking the button below:</p>
                <a href="https://aviatoinvitation-bhaskar9221.redoc.ly/" class="button">View API Documentation</a>
                <a href="https://github.com/bhaskar9221/Aviato-bhaskar9221-ML" class="button">View GitHub Repository</a>
                <a image="https://raw.githubusercontent.com/bhaskar9221/Aviato-bhaskar9221-ML/main/FirestoreDB.png" class="button">View FireStore Database Screenshot</a>

                

                <p>{message}</p>
                <p>I have also set up an GCP Free Tier Accound, and used it for deployment, and GCP FirseStore for the database.</p>
                <p>I appreciate your time and look forward to your feedback.</p>
            </div>
            <div class="footer">
                <p>Thank you,<br>Bhaskar Mondal -bhaskar9221@ML</p>
                <p>If you have any questions, feel free to reply to this email.</p>
            </div>
        </div>
    </body>
    </html>
    """

    msg.attach(MIMEText(html_content, "html"))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.sendmail(smtp_username, to_email, msg.as_string())
        server.quit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/send_invitation")
async def send_email_endpoint():
    subject = "API Documentation Invitation by Bhaskar Mondal"
    message = "Hello Ma'am, I am Bhaskar. Here are the API invitation emails, requested as per the task."
    email_list = ["shraddha@aviato.consulting","pooja@aviato.consulting","prijesh@aviato.consulting","hiring@aviato.consulting","bhaskarmondal7221@gmail.com"]
    #friend = ["abhijeetjoy14@gmail.com","bhaskarmondal.vef@gmail.com"]
    try:
        for email in email_list:
            send_email(email, subject, message)
            
        return {"message": "Email sent successfully"}
    except HTTPException as e:
        raise HTTPException(status_code=500, detail=f"Error sending email: {e.detail}")





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
