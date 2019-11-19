from django import forms
from .models import Job, City


"""
class CityNameForm(forms.Form):
    city_name = forms.CharField()
    
    slug = forms.SlugField()
    content = forms.CharField(widget = forms.Textarea)
"""


class JobModelForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(JobModelForm, self).__init__(*args, **kwargs)
        qs = City.objects.all()
        qs = City.objects.filter(country__name="España")
        techlist = (
            ('freighters', 'Freighters'),
            ('fighters', 'Fighters'),
            ('corvettes', 'Corvettes'),
            ('light_cruisers', 'Light Cruisers'),
            ('destroyers', 'Destroyers'),
            ('frigates', 'Frigates'),
            ('heavy_cruisers', 'Heavy Cruisers'),
            ('battlecruisers', 'Battlecruisers'),
            ('battleships', 'Battleships'),
            ('dreadnoughts', 'Dreadnoughts')
        )

        #self.fields["ship_choice"] = forms.ChoiceField(choices=choicelist)
        self.fields["cities"] = forms.ModelChoiceField(queryset=qs)

    #new_attribute = forms.CharField(widget=forms.Textarea)
    #area = forms.CharField()

    class Meta:
        model = Job
        fields = ['type', 'working_day', 'category_level', 'area', 'province', 'cities']
        #field_classes = {'cities': forms.CharField()}
        # Error: widgets = {'cities': forms.CharField()}




