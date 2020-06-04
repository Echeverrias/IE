from django import forms
from django.forms import ValidationError
from django.core import exceptions
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.core.validators import validate_email
from django.utils.translation import ugettext, ugettext_lazy as _

class RegisterForm(UserCreationForm):

    username = forms.CharField(label=_("Nombre de usuario"),
                               error_messages={'required': _('Introduce el nombre de usuario.'),
                                })
    email = forms.EmailField(label=_("Dirección de correo electrónico"),
                            error_messages={
                                'required': _('Introduce la dirección de correo electrónico.'),
                                'invalid': _('La dirección de correo electrónico no es válida.'),
                             })
    password1 = forms.CharField(label=_("Contraseña"),
                                help_text=_("<ul><li>La contraseña no debe ser parecida al nombre de usuario.</li>\
                                <li>La contraseña debe de tener al menos 8 caracteres</li>\
                                <li>La contraseña no puede ser usual</li>\
                                <li>La contraseña no puede ser solamente numérica.</li></ul>")
                                , error_messages={
                                    'required': _('Introduce la contraseña.'),
                                    'invalid': _('La contraseña no es válida.'),
                                })
    password2 = forms.CharField(label=_("Confirmación de contraseña"),
                                help_text=_("Introduce de nuevo la misma contraseña."),
                                error_messages={
                                    'required': _('Introduce la contraseña de confirmación.'),
                                    'password_mismatch': _("Las contraseñas no coinciden."),
                                })

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def _translate_password_errors(self):
        d = {
            'This password is too short. It must contain at least 8 characters.': 'La contraseña debe de tener al menos 8 caracteres.',
            'This password is too common.': 'La contraseña es demasiado común.',
            'The two password fields didn’t match.': 'Las contraseñas no coinciden.',
            'This password is entirely numeric.': 'La contraseña es enteramente numérica.',
            'The password is too similar to the username.': 'La contraseña es demasiado parecida al nombre de usuario.'

        }
        errors = self.errors.get('password2', None)
        if errors:
            errors_ = [d.get(error, error) for error in errors]
            self.errors['password2'] = errors_

    def _post_clean(self):
        try:
            super(RegisterForm, self)._post_clean()
            self._translate_password_errors()
        except Exception as e:
            raise e

    def clean_email(self):
        email = self.cleaned_data.get('email')
        try:
            validate_email(email)
        except exceptions.ValidationError as e:
            raise ValidationError('El email no es válido')
        if User.objects.filter(email__exact=email):
            raise ValidationError('El email está asociado a otro usuario')
        else:
            return email


class LoginForm(AuthenticationForm):


    username = forms.CharField(label=_("Nombre de usuario"),
                               error_messages={'required': _('Introduce el nombre de usuario.'),
                                })
    password = forms.CharField(label=_("Contraseña"),
                                error_messages={
                                    'required': _('Introduce la contraseña.'),
                                    'invalid': _('La contraseña no es válida.'),
                                })

    class Meta:
        model = User
        fields = ('username', 'password')