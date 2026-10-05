from fastapi import FastAPI, Path, Query, HTTPException
import json

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

@app.get('/patient/{patient_id}')
def view_patient(patient_id:str = Path(...,description='patient id in DB', examples='7')):
    data = get_Data();

    if patient_id in data:
        return data[patient_id]
    
    #return{'error': 'patient not found'}
    raise HTTPException(status_code=404, detail='patient not found')

@app.get('/sort')
def sort_patient(sort_by:str = Query(...,description='sort by'),order:str = Query(...,description='order')):
    valid_fields =['height','weight','bmi']

    if sort_by not in valid_fields:
        raise HTTPException(status_code=400, detail=f'invalid field, select from {valid_fields}')
    
    if order not in ['asc','desc']:
        raise HTTPException(status_code=400, detail='invalid fields, select from asc or desc')

    data = get_Data()
    seq = True if order=='desc' else False

    sorted_data = sorted(data.values(), key=lambda patient: patient.get(sort_by,order), reverse=seq)
    
    return sorted_data