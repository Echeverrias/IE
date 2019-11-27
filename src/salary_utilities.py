from utilities import (
    get_int_list_from_string,
    get_text_before_sub,
)
from jobs.models import Job
from django.db.models import Q



def get_annual_salary(text):
    KEYS = {
        'year': ['bruto anual', 'b/a', 'bruto al año'],
        'month': ['bruto mensual', 'b/m', 'bruto al mes'],
        'day': ['bruto al día', 'b/d', 'bruto al día'],
    }
    salary = []
    if text:
        salary_type_tl = [(sub, text.find(sub)) for sub in KEYS['year'] if text.find(sub) > 0]
        if salary_type_tl:
            is_monthly_salary = False
        else:
            salary_type_tl = [(sub, text.find(sub)) for sub in KEYS['month'] if text.find(sub) > 0]
            is_monthly_salary = True
        if salary_type_tl:
            i_salary = max(0, text.lower().find('salar'))
            if i_salary == 0:
                text_ = get_text_before_sub(text, salary_type_tl[0][0], distance=25, separators=['\n', '\r'])
            else:
                text_ = text[i_salary:salary_type_tl[0][1]]
            salary = get_int_list_from_string(text_)
            if salary and is_monthly_salary:
                salary = [i*12 for i in salary]
    return salary