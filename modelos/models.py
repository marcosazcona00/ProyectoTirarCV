from django.contrib.auth.models     import User
from django.db                      import models
from datetime                       import datetime
from model_utils.managers           import InheritanceManager

# Create your models here.

class Idioma(models.Model):
    class Meta: 
        db_table = 'idioma'

    nombre = models.CharField(max_length = 15)
    
    def __str__(self):  
        return self.nombre

class Tipo_Empleo(models.Model):
    class Meta:
        db_table = 'tipo_empleo'
    nombre_tipo = models.CharField(unique = True,max_length = 255)
    #tipos = models.ManyToManyField('self',related_name = 'tipos_empleo',symmetrical=False,db_table='tipos',blank = True)

    def __str__(self):
        return self.nombre_tipo


class Usuario(models.Model):
    class Meta:
        db_table = 'usuario'
    objects = InheritanceManager()
    usuario = models.OneToOneField(User,unique = True,on_delete = models.CASCADE)

    def user(self):
        """
        Devuelve al User con el que esta asociado
        :param:
        :return: User
        """
        return User.objects.get(id = self.usuario_id)

    def es_empleado(self):
        pass

class Empleado(Usuario):
    class Meta:
        db_table = 'empleado'
    cv = models.FileField(null = True)
    anios_experiencia = models.IntegerField(null = True)
    idioma = models.ManyToManyField(Idioma,db_table = 'idiomas_empleado',blank = True)
    tipos_empleos_interes = models.ManyToManyField(Tipo_Empleo,db_table = 'interes_tipo_empleo',blank = True)

    def idiomas(self):
        return self.idioma.all()

    def tiene_idiomas(self):
        return True if self.idioma.all() else False

    def es_empleado(self):
        return True

    def empleos_aplicados(self):
        solicitudes = SolicitudEmpleo.objects.filter(empleado = self)
        return Empleo.objects.filter(id__in = solicitudes.values('empleo_id'))

class Empleador(Usuario):
    class Meta:
        db_table = 'empleador'

    def es_empleado(self):
        return False

class Empleo(models.Model):
    class Meta:
        db_table = 'empleo'
    empleador = models.ForeignKey(Empleador,on_delete = models.DO_NOTHING)
    tipo_empleo = models.ManyToManyField(Tipo_Empleo,db_table = 'tipos_empleo_asociados')
    idioma = models.ManyToManyField(Idioma,blank = True,db_table = 'idiomas_empleo')
    descripcion = models.CharField(max_length = 255)
    anios_experiencia = models.IntegerField()
    fecha_publicacion = models.DateTimeField(default=datetime.now, blank=True)

    def idiomas(self):
        return self.idioma.all()

    def solicitudes(self):
        return SolicitudEmpleo.objects.filter(empleo = self, aceptado = False)
        
class SolicitudEmpleo(models.Model):
    class Meta:
        db_table = 'solicitud_empleo'
    empleo = models.ForeignKey(Empleo,on_delete = models.CASCADE)
    empleado = models.ForeignKey(Empleado,on_delete = models.CASCADE)
    aceptado = models.BooleanField()
