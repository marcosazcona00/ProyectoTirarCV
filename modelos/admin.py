from modelos.models import Tipo_Empleo,Idioma
from django.contrib import admin

# Register your models here.

class IdiomaAdmin(admin.ModelAdmin):    
    fields = (('nombre'),)
    def niveles(self):
        return Nivel.objects.all()

    def save_model(self, request, obj, form, change):
        "Guarda todos los niveles (Basico,Intermedio y Avanzado) al nuevo idioma ingresado"
        super().save_model(request, obj, form, change)
        for nivel in self.niveles():
            obj.nivel.add(nivel)

admin.site.register(Tipo_Empleo)
admin.site.register(Idioma,IdiomaAdmin)