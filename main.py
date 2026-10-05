from fastapi import FastAPI, Path, Query, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, computed_field
from typing import Annotated, Literal, Optional
import json

app = FastAPI()
# Pydantic model for creating a new user or patient in the database
class patient(BaseModel):

    id : Annotated[str, Field(..., description='ID of the patient', exampe='p001')]
    name: Annotated[str, Field(...,description='Name of the patient')]
    city: Annotated[str, Field(...,description='City where patient lives')]
    age: Annotated[int, Field(...,gt=0, lt=120, description='Age of the patient')]
    gender: Annotated[Literal['male','female','others'], Filed(...,description='Gender of the patient')]
    height: Annotated[float, Field(...,gt=0, description='Height of the patient in meters')]
    weight: Annotated[float, Field(...,gt=0, description='Weight of the patient in kg')]

    @computed_field
    @property
    def bmi(self) -> float:
        bmi = round(self.weight/((self.height / 100) **2),2)
        return bmi


    @computed_field
    @property
    def verdict(self) -> str:

        if self.bmi < 18.5 :
            return 'underweight'
        elif self.bmi > 25 :
            return 'overweight'
        else :
             return 'Normal'

# Pydantic model to update the existing user data in database
class patientUpdate(BaseModel):
    name : Annotated[Optional[str], Field(default=None)]
    city: Annotated[Optional[str], Field(default=None)]
    age: Annotated[Optional[int], Field(default=None, gt=0, lt=120)]
    gender: Annotated[Optional[Literal['male','female','others']], Field(default=None)]
    height: Annotated[Optional[float], Field(default=None, gt=0)]
    weight: Annotated[Optional[float], Field(default=None, gt=0)]
    
# Utility functions for fetching and updating the data into database
def get_Data():
    with open('patient.json','r') as f:
        data = json.load(f)

        return data

def save_Data(data):
    with open('patient.json', 'w') as f:
        json.dump(data, f)

# These are the endpoints 
@app.get('/')
def home():
    return {"message":"patient management system"}

@app.get('/about')
def home():
    return {'message':'A fully function API to manage your patient records'}

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

@app.post('/create')
def create_patient(newPatient: patient):

    data = get_Data()

    if newPatient.id in data:
        raise HTTPException(status_code=400, detail='Patient already exist')
    
    data[newPatient.id] = newPatient.model_dump(exclude=['id'])
    
    save_Data(data)

    return JSONResponse(status_code=201, content={'message':'Patient created successfully'})

@app.put('/update/{patient_id}')
def updatePatient(patient_id: str, patientInfo:patientUpdate):
    data = get_Data()
    # Check if the patient id is in data or not  
    if patient_id in data:
        #if yes then we fetch existing patient data from database
        existing_patient_info = data[patient_id]
        # fetch updated fields from our patientUpdate pydantic class
        updated_patient_info = patientInfo.model_dump(exclude_unset=True)
        # Create a for loop where for same key we change the values iteratively
        for key, value in updated_patient_info.items():
            existing_patient_info[key] = value
        # Now in exisiting info we add patient id     
        existing_patient_info['id'] = patient_id
        # We create a Patient class pydantic object using existing patient detail which are now updated with new details after the for loop
        existing_patient_pydantic_obj = patient(**existing_patient_info)
        #now after that model dump the Patient pydantic object data into same variable which is exisitng patient
        existing_patient_info = existing_patient_pydantic_obj.model_dump(exclude={'id'})
        # Replace the data in database.
        data[patient_id] = existing_patient_info
        # Save the data permanently 
        save_Data(data)
        return JSONResponse(status_code=200, content={'message': 'Patient details are updated successfully'})
        
    else:
        raise HTTPException(status_code=404, detail='patient id does not exist')

@app.delete('/delete/{patient_id}')
def deletePatient(patient_id: str):
    data = get_Data()
    if patient_id not in data:
        raise HTTPException(status_code=404, detail='patient id not found')
    
    # data.pop(patient_id, None) -> this line also can delete the data and return the deleted data if you want to save in a variable 
    del data[patient_id]
    save_Data(data)
    return JSONResponse(status_code=200, content={'message':'patient deleted successfully'})