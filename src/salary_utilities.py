from utilities import get_int_list, get_text_before_sub
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
            salary = get_int_list(text_)
            if salary and is_monthly_salary:
                salary = [i*12 for i in salary]
    return salary

def yyy():
    qs = Job.objects.filter(Q(minimum_salary__gt=0)&Q(maximum_salary__gt=0)&~Q(it_is_offered=""))
    for j in qs:

        salary = get_annual_salary(j.it_is_offered)
    return salary

def yyy():
    qs = Job.objects.filter(Q(minimum_salary__gte=1)&Q(minimum_salary__lte=9))
    s = set()
    for j in qs:

        salary = get_annual_salary(j.it_is_offered)
        if salary:
            print((j.minimum_salary, j.maximum_salary))
            print((j.minimum_years_of_experience, j.recommendable_years_of_experience))
            print(j.link)
            print(j.contract)
            print();print();
            s.add(j.contract)
    print(s)
    print(len(qs))
    return salary