from modelos.models                 import *
from django.contrib.auth.models     import User
from datetime                       import datetime
from django.test                    import TestCase,Client
from django.urls                    import reverse

from django.contrib.auth import authenticate,login
# Create your tests here.

class SetUpEmpleo(TestCase):
    def setUp(self):
        self.cliente = Client()
        self.informatica = Tipo_Empleo(nombre_tipo = 'Informatica')
        self.informatica.save()
        self.profesor = Tipo_Empleo(nombre_tipo = 'Profesor')
        self.profesor.save()
        self.investigacion = Tipo_Empleo(nombre_tipo = 'Investigacion')
        self.investigacion.save()
        self.ingles = Tipo_Empleo(nombre_tipo = 'Ingles')
        self.ingles.save()

        self.empleo1 = Empleo(
            empleador = self.empleador,
            descripcion = '',
            anios_experiencia = 2,
            fecha_publicacion = datetime.now()
        )
        self.empleo1.save()
        self.empleo1.tipo_empleo.add(self.informatica)

        self.empleo2 = Empleo(
            empleador = self.empleador,
            descripcion = '',
            anios_experiencia = 3,
            fecha_publicacion = datetime.now()
        )
        self.empleo2.save()
        self.empleo2.tipo_empleo.add(self.profesor)

class TestEmpleador(SetUpEmpleo):
    def setUp(self):
        self.user = User.objects.create_user(username = 'empleador1',password='123')
        self.user.save()
        self.empleador = Empleador(
            usuario_id = self.user.id,
        )
        self.empleador.save()
       
        super(TestEmpleador,self).setUp()

    def test_login(self):
        self.assertIs(self.client.login(username = 'empleador1',password='123'),True)
        self.assertIs(self.client.login(username = 'empleador1',password='124'),False)
        self.assertIs(self.client.login(username = 'pepe',password='123'),False)
        
    def test_es_empleador(self):
        user_id = User.objects.get(username = 'empleador1').id
        empleador = Usuario.objects.get_subclass(usuario_id = user_id)
        self.assertIs(empleador.es_empleado(),False)

    def test_sus_empleos(self):
        empleos = list(Empleo.objects.filter(empleador = self.empleador))
        self.assertEqual(len(empleos),2)
    
class TestEmpleado(SetUpEmpleo):
    def setUp(self):
        self.user = User.objects.create_user(username = 'empleador1',password='123')
        self.user.save()
        self.empleador = Empleador(
            usuario_id = self.user.id,
        )
        self.empleador.save()
        self.user = User.objects.create_user(username = 'marcosAzcona12300',password='123')
        self.user.save()
        self.empleado = Empleado(
            usuario_id = self.user.id,
            anios_experiencia = 6,
            cv = 'curriculim.pdf'
        )
        self.empleado.save()

        self.basico = Nivel(
            nivel = 'Basico'                    
        )
        self.basico.save()

        self.idioma_ingles = Idioma(
            nombre = 'Ingles'
        )
        self.idioma_ingles.save()
        self.idioma_ingles.nivel.add(self.basico)

        self.idioma_frances = Idioma(
            nombre = 'Frances'
        )
        self.idioma_frances.save()
        self.idioma_frances.nivel.add(self.basico)

        super(TestEmpleado,self).setUp()

 
    def test_es_empleado(self):
        user_id = User.objects.get(username = 'marcosAzcona12300').id
        empleado = Usuario.objects.get_subclass(usuario_id = user_id)
        self.assertIs(empleado.es_empleado(),True)
     
    def test_login(self):
        self.assertIs(self.client.login(username = 'marcosAzcona12300',password='123'),True)
        self.assertIs(self.client.login(username = 'marcosAzcona12300',password='124'),False)
        self.assertIs(self.client.login(username = 'marcosAzcona12301',password='123'),False)

    def test_resultado_busqueda(self):
        "Se testea el resultado sin que el usuario tenga idioma asociado"
        self.client.login(username='marcosAzcona12300',password='123')
        response = self.client.get('/busqueda_empleo/',{'criterio_busqueda': ['Informatica']})
        resultados = response.context['object_list'].object_list
        self.assertEqual(resultados, [self.empleo1])

        response = self.client.get('/busqueda_empleo/',{'criterio_busqueda': ['Informatica','Profesor']})
        resultados = response.context['object_list'].object_list
        self.assertEqual(resultados, [self.empleo1,self.empleo2])

        self.empleo1.tipo_empleo.add(self.profesor)
        response = self.client.get('/busqueda_empleo/',{'criterio_busqueda': ['Profesor']})
        resultados = response.context['object_list'].object_list
        self.assertEqual(resultados, [self.empleo1,self.empleo2])

    def test_resultado_busqueda_con_idioma(self):
        "Se testea teniendo el usuario idioma asociado"
        self.client.login(username='marcosAzcona12300',password='123')

        self.empleo1.idioma.add(self.idioma_ingles)

        response = self.client.get('/busqueda_empleo/',{'criterio_busqueda': ['Informatica']})
        resultados = response.context['object_list'].object_list
        self.assertEqual(resultados, [self.empleo1])

        self.empleo3 = Empleo(
            empleador = self.empleador,
            descripcion = '',
            anios_experiencia = 3,
            fecha_publicacion = datetime.now()
        )

        self.empleo3.save()
        self.empleo3.tipo_empleo.add(self.investigacion)
        response = self.client.get('/busqueda_empleo/',{'criterio_busqueda': ['Informatica','Profesor','Investigacion']})
        resultados = response.context['object_list'].object_list
        self.assertEqual(resultados,[self.empleo1,self.empleo2,self.empleo3])

        self.empleado.idioma.add(self.idioma_ingles)
        response = self.client.get('/busqueda_empleo/',{'criterio_busqueda': ['Informatica','Profesor','Investigacion']})
        resultados = response.context['object_list'].object_list
        self.assertEqual(resultados,[self.empleo1,self.empleo2,self.empleo3])

        self.empleo3.idioma.add(self.idioma_frances)
        response = self.client.get('/busqueda_empleo/',{'criterio_busqueda': ['Informatica','Profesor','Investigacion']})
        resultados = response.context['object_list'].object_list
        self.assertEqual(resultados,[self.empleo1,self.empleo2])

        self.empleado.idioma.add(self.idioma_frances)
        response = self.client.get('/busqueda_empleo/',{'criterio_busqueda': ['Informatica','Profesor','Investigacion']})
        resultados = response.context['object_list'].object_list
        self.assertEqual(resultados,[self.empleo1,self.empleo3,self.empleo2])


    def test_resultado_busqueda_vacia(self): 
        self.client.login(username='marcosAzcona12300',password='123')
        response = self.client.get('/busqueda_empleo/',{'criterio_busqueda': ['Ingles']})
        resultados = response.context['object_list'].object_list
        self.assertEqual(list(resultados),[])

