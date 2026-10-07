from django.shortcuts import render
import joblib
import numpy as np
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, 'models')

ensemble_model = joblib.load(os.path.join(MODEL_DIR, 'ensemble_model.pkl'))

FEATURES = [
    'fever', 'nausea', 'diarrhoea', 'asthenia_weakness', 'loss_of_appetite',
    'abdominal_pain', 'chest_pain', 'bone_muscle_pain', 'joint_pain', 'headache',
    'cough', 'breathlessness', 'swallowing_problem', 'sorethroat', 'jaundice',
    'conjunctivitis', 'skin_rash', 'hichups', 'pain_eyes_sensitivity_light',
    'coma', 'confused_disoriented', 'bleeding', 'bleeding_gum',
    'bleeding_injection_site', 'epistaxis', 'melenas', 'bleeding_vomit',
    'vomito_negro', 'hemoptisis', 'bleeding_vagina', 'purpura', 'bleeding_urine',
    'bleeding_other', 'contact_EVD_case', 'contact_funeral', 'contact_travel',
    'contact_HF', 'contact_tradi', 'contact with animal', 'sex', 'age',
    'Profession'
]

def index(request):
    return render(request, 'index.html')

def predict(request):
    if request.method == 'POST':
        try:
            input_data = []
            for feature in FEATURES:
                val = request.POST.get(feature, 0)
                input_data.append(float(val))

            input_array = np.array([input_data])
            prediction = ensemble_model.predict(input_array)[0]
            probabilities = ensemble_model.predict_proba(input_array)[0]
            confidence = round(max(probabilities) * 100, 2)

            if prediction == 1:
                result = 'Positive'
                result_class = 'danger'
                message = 'High risk of Ebola Virus Disease detected. Please seek immediate medical attention.'
            else:
                result = 'Negative'
                result_class = 'success'
                message = 'Low risk of Ebola Virus Disease detected. Continue monitoring symptoms.'

            context = {
                'prediction': result,
                'result_class': result_class,
                'confidence': confidence,
                'message': message,
                'submitted': True,
                'post_data': request.POST,
            }
            return render(request, 'index.html', context)
        except Exception as e:
            context = {
                'error': f'Prediction error: {str(e)}',
                'submitted': True,
            }
            return render(request, 'index.html', context)

    return render(request, 'index.html')




