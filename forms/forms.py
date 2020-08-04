from modelos.models                 import *
from django.contrib.auth.models     import User
from django                         import forms        
from django.forms                   import Form,ModelForm
from django.contrib.auth.forms      import AuthenticationForm


class RegistroEmpleadoForm(forms.Form):
    def __init__(self,*args,**kwargs):
        super(RegistroEmpleadoForm,self).__init__(*args,**kwargs)
        self.fields['username'] = forms.CharField()
        self.fields['first_name'] = forms.CharField()
        self.fields['last_name'] = forms.CharField()
        self.fields['email'] = forms.CharField()
        self.fields['password'] = forms.CharField()
        self.fields['cv'] = forms.FileField()
        self.fields['anios_experiencia'] = forms.IntegerField()
        self.extensiones = ['pdf','docx']

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username = username).exists():
            raise forms.ValidationError('El nombre de usuario '+ username + ' ya se encuentra registrado')
        return username
        
    def clean_cv(self):
        cv = self.cleaned_data['cv']
        extension = str(cv).split('.')[-1]
        if extension not in self.extensiones:
            raise forms.ValidationError('La extension '+ extension +' no es valida') 
        return cv

class RegistroEmpleadorForm(forms.Form):
    def __init__(self,*args,**kwargs):
        super(RegistroEmpleadorForm,self).__init__(*args,**kwargs)
        self.fields['username'] = forms.CharField()
        self.fields['first_name'] = forms.CharField()
        self.fields['last_name'] = forms.CharField()
        self.fields['email'] = forms.CharField()
        self.fields['password'] = forms.CharField()

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username = username).exists():
            raise forms.ValidationError('El nombre de usuario '+ username + ' ya se encuentra registrado')
        return username

class InicioSesionForm(AuthenticationForm):
    error_messages = {
        'invalid_login': 'Los datos ingresados son incorrectos'
    }

class ActualizarEmpleadoForm(ModelForm):
    class Meta:
        model = Empleado
        fields = ['cv','anios_experiencia','idioma','tipos_empleos_interes']
        
    def __init__(self,*args,**kwargs):
        super(ActualizarEmpleadoForm,self).__init__(*args,**kwargs)
        self.fields['username'] = forms.CharField(show_hidden_initial = True)
        self.fields['first_name'] = forms.CharField(show_hidden_initial = True)
        self.fields['last_name'] = forms.CharField(show_hidden_initial = True)
        self.fields['email'] = forms.CharField(show_hidden_initial = True)
        self.extensiones = ['pdf','docx']

    def __cambio_valor(self,campo,valor_campo):
        """
        Determina si el valor cambio con respecto al inicial
        param campo: String
        param valor_campo: Field
        return: Boolean
        """
        return self.initial[campo] != valor_campo

    def clean_username(self):
        username = self.cleaned_data['username']
        if self.__cambio_valor('username',username):
            if User.objects.filter(username = username).exists():
                raise forms.ValidationError('Ya existe el nombre de usuario')
        return username
    
    def clean_cv(self):
        cv = self.cleaned_data['cv']
        if self.__cambio_valor('cv',cv):
            extension = str(cv).split('.')[-1]
            if extension not in self.extensiones:
                raise forms.ValidationError('La extension '+ extension +' no es valida') 
        return cv
        
class CargaEmpleoForm(ModelForm):
    class Meta:
        model = Empleo
        fields = ['tipo_empleo','descripcion','anios_experiencia','idioma']
        widgets = {
            'descripcion': forms.Textarea(attrs={'cols': 40, 'rows': 10}),
        }
    