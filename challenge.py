import pandas as pd
import json
import traceback

bodyMassFormula = '''
BMI=WeightKg/((HeightCm/100)**2)
'''

countCategory = 'Overweight'

Categories = [
        'Underweight', 
        'Normal weight',
        'Overweight',
        'Moderately obese', 
        'Severely obese',
        'Very severely obese'
        ]

Risks = [
        'Malnutrition risk', 
        'Low risk',
        'Enhanced risk',
        'Medium risk', 
        'High risk',
        'Very high risk'
        ]

categoryGroup = [-0.1,18.49,24.9,29.9,34.9,39.9]

def categorise(bmi):
    labelsCategory = Categories[:-1]

    labelsRisk = Risks[:-1]

    bmiCategory = pd.cut(bmi, categoryGroup, labels=labelsCategory)
    bmiRisk = pd.cut(bmi, categoryGroup, labels=labelsRisk)
    return bmiCategory, bmiRisk

def lambda_handler(event=None, context=None):
    try:
        assert len(categoryGroup) == len(Risks) == len(Categories), 'Length of categoryGroup, Risks and Categories should be equal'
        assert countCategory in Categories, 'countCategory not defined in Categories'
        df = pd.DataFrame(event) 
        df = df.dropna()
        df.eval(bodyMassFormula,inplace=True)
        bmiCategory, bmiRisk = categorise(df.BMI)
        df.insert(loc=len(df.columns), column='BMI Category', value=bmiCategory)
        df.insert(loc=len(df.columns), column='Health risk', value=bmiRisk)
        df['BMI Category'] = df['BMI Category'].cat.add_categories(Categories[-1])
        df['BMI Category'] = df['BMI Category'].fillna(Categories[-1])
        df['Health risk'] = df['Health risk'].cat.add_categories(Risks[-1])
        df['Health risk'] = df['Health risk'].fillna(Risks[-1])
        count = df['BMI Category'].value_counts()[countCategory]
        op = {'data': df.to_dict(orient='records'), 'count':count}
        message = op
        status = True
    except:
        message = 'Something went wrong'
        status = False
        e = traceback.format_exc()
        print(e)
        print('Saving error in errorLog file.........')
        with open('errorLog','a') as errorLog:
            errorLog.write(e)
    return {
        'output': message,
        'status': status
    }

event = [
    {"Gender": "Male", "HeightCm": 171, "WeightKg": 96},
    {"Gender": "Male", "HeightCm": 161, "WeightKg": 85},
    {"Gender": "Male", "HeightCm": 180, "WeightKg": 77},
    {"Gender": "Female", "HeightCm": 166, "WeightKg": 62},
    {"Gender": "Female", "HeightCm": 150, "WeightKg": 70},
    {"Gender": "Female", "HeightCm": 167, "WeightKg": 82}
]

try:
    with open('input.json', 'r') as f:
        event = f.read()
    event = json.loads(event)['data']
except:
    print('Input not in proper format hence using predertermined input..........')

print(lambda_handler(event=event))