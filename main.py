from fastapi import FastAPI

app = FastAPI()

# This is utility function used to fetch data from JSON file
def get_Data():
    with open('patient.json','r') as f:
        data = json.load(f)

        return data

@app.get('/')
def home():
    return {'message':'Welcome To Home Page'}

# This route used to display all the patient in the DB or JSON file for now
@app.get('/patient')
def view():
    data = get_Data();
    return data