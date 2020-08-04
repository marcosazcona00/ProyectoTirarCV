from modelos.models                     import *
from forms.forms                        import * 
from django.views                       import View
from django.contrib.auth                import logout
from django.urls                        import reverse
from django.core.paginator              import Paginator
from django.db.models                   import Q,Exists
from datetime                           import datetime
from django.views.generic.list          import ListView
from django.views.generic               import DetailView
from django.views.decorators.csrf       import csrf_exempt
from django.views.generic.base          import TemplateView
from django.shortcuts                   import render,redirect
from django.core.files.storage          import FileSystemStorage
from django.contrib.auth                import authenticate, login
from django.contrib.auth.views          import LoginView, LogoutView
from django.views.generic.edit          import CreateView, FormView,DeleteView,UpdateView

def guardar_imagen(cv):
    if cv is not None:
        fs = FileSystemStorage()
        fs.save(cv.name, cv)

def guardar_usuario(form):
    user = User.objects.create_user(
        username = form.cleaned_data['username'],
        password = form.cleaned_data['password'],
        first_name = form.cleaned_data['first_name'],
        last_name = form.cleaned_data['last_name'],
        email = form.cleaned_data['email'],
    )
    user.save()    

def cargar_empleo(request):
    empleador_id = Usuario.objects.get(usuario_id = request.session['_auth_user_id']).id
    empleo = Empleo(
        empleador_id =  empleador_id,
        descripcion = request.POST['descripcion'],
        fecha_publicacion = datetime.now(),
        anios_experiencia = int(request.POST['anios_experiencia'])
    )
    empleo.save()
    for tipo_empleo in dict(request.POST)['tipo_empleo']:
        empleo.tipo_empleo.add(tipo_empleo)
    
    try:
        "Agregamos los id de los idiomas al empleo, los cuales son opcionales"
        for id_idioma in dict(request.POST)['idioma']:
            empleo.idioma.add(id_idioma)
    except:
        pass
    return redirect(reverse('home_empleador'))

def aplicar_empleo(request,id_empleo):
    empleado = Usuario.objects.get_subclass(usuario_id = request.session['_auth_user_id'])
    solicitud = SolicitudEmpleo(
        empleado_id = empleado.id,
        empleo_id = id_empleo,
        aceptado = False
    )
    solicitud.save()
    return redirect('/')

def aceptar_entrevista(request,id_solicitud):
    solicitud = SolicitudEmpleo.objects.get(id = id_solicitud)
    solicitud.aceptado = True
    solicitud.save()
    return redirect(reverse('home'))

def empleos_interesados(empleado):
    """
    Devuelve una lista de empleos que sean de interes para el empleado segun lo que puso en sus intereses
    param empleado: Empleado
    return Empleado[*]
    """
    idiomas = Idioma.objects.all()
    idiomas_empleado = empleado.idiomas()
    empleado_tipos_empleos = empleado.tipos_empleos_interes.all()
    
    "Las solicitudes del empleado que aun no fueron aceptadas"
    solicitudes_en_espera = SolicitudEmpleo.objects.filter(empleado = empleado,aceptado = False)
    
    """
    Tomamos aquellos empleos que tengan menos anios de experiencia que el empleado (89), que los tipos del empleo este entre
    los que eligio el empleado (90), que la solicitud del empleo aun no haya sido aceptada (01),
    Si no tiene idiomas, que tome ese empleo (95 Q(idioma = None)), 
    O si tiene idiomas, que tenga los del empleado,si el empleado eligio idioma (95 parte del OR)
    """
    if solicitudes_en_espera:
        print('hola')
    empleos_de_interes = Empleo.objects.filter(
        Q(
        anios_experiencia__lte = empleado.anios_experiencia,
        tipo_empleo__in = empleado_tipos_empleos,
        #id__in = solicitdes_en_espera.values('empleo_id') if solicitudes_en_espera else empleado_tipos_empleos
        ),
        (
            Q(idioma = None) | Q(idioma__in = idiomas_empleado if empleado.tiene_idiomas() else idiomas) 
            
        )
    ).distinct()

    return empleos_de_interes
    
class Busqueda_Empleo(View):
    def __init__(self):
        self.resultados = None
    
    def get(self,request):
        "La idea era dejar cargada en la sesion el diccionario que se me crea al buscar trabajo, porque entre vistas al pasar de pagina se pierde"
        "Si el diccionario no vino vacio"
        if 'criterio_busqueda' in dict(request.GET):
            "Si ya existe la clave, actualizamos la sesion"
            request.session['criterio_busqueda'] = dict(request.GET)
          
        inputs_busqueda = request.session['criterio_busqueda']
        self.resultados = self.resultados_busqueda(inputs_busqueda)
        

        paginator = Paginator(self.resultados, 4)     
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        empleado = Usuario.objects.get_subclass(usuario_id = self.request.session['_auth_user_id'])
        contexto = {
            'object_list': page_obj, 
            'page_obj': page_obj,
            'tipos_empleos': Tipo_Empleo.objects.all(),
            'empleado':empleado,
            'empleos_aplicados': SolicitudEmpleo.objects.filter(empleado = empleado)
        
        }      
        return render(request,'listado_empleos_empleado.html',contexto)

    def listado_tipos_empleos(self,tipos):
        "Devuelve una lista de los modelos Tipo_Empleo elegidos"
        tipos_empleos = list()
        for tipo in tipos:
            tipos_empleos.append(Tipo_Empleo.objects.get(nombre_tipo = tipo))
        return tipos_empleos

    def resultados_busqueda(self,inputs_busqueda):
        "Retorna el querySet de empleos"
        usuario_id = Usuario.objects.get(usuario_id = self.request.session['_auth_user_id']).id
        empleado = Empleado.objects.get(usuario_ptr_id = usuario_id)
        tipos_empleos = self.listado_tipos_empleos(inputs_busqueda['criterio_busqueda'])

        empleos =  Empleo.objects.filter(
            tipo_empleo__in = tipos_empleos,anios_experiencia__lte = empleado.anios_experiencia
        ).distinct()

        if empleado.tiene_idiomas():
            empleos_con_idiomas = empleos.exclude(idioma = None)
            "Filtramos los empleos que tengan los idiomas del empleado"
            empleos_con_idiomas = empleos_con_idiomas.filter(idioma__in = list(empleado.idiomas()))
            "Los unimos con los empleos que no tienen idiomas asignados"
            empleos = empleos_con_idiomas.union(empleos.filter(idioma=None))
        return empleos

class InicioView(View):
    def get(self,request):
        if not request.user.is_authenticated:    
            return render(request,'inicio.html')
        else:
            usuario = Usuario.objects.get_subclass(usuario_id = request.user.id) #Me devuelve la subclase, sea empleado o empleador
            if usuario.es_empleado():
                return redirect('/home_empleado/')
            else:
                return redirect('/home_empleador/') 

class RegistroEmpleadoView(FormView):
    form_class = RegistroEmpleadoForm
    template_name = 'registro_empleado.html'

    def form_valid(self,form):
        guardar_usuario(form)
        self.guardar_tipo_empleado(form)
        return redirect(reverse('home'))


    def guardar_tipo_empleado(self,form):
        cv = form.cleaned_data['cv']
        guardar_imagen(cv)
        #Para no tener conflictos, con instanciar al hijo ya es suficiente
        empleado = Empleado(
            usuario_id = User.objects.get(username = form.cleaned_data['username']).id,
            cv = cv,
            anios_experiencia = form.cleaned_data['anios_experiencia']
        )
        empleado.save()
        
class RegistroEmpleadorView(FormView):
    form_class = RegistroEmpleadorForm
    template_name = 'registro_empleador.html'

    def form_valid(self,form):
        guardar_usuario(form)
        self.guardar_tipo_empleado(form)
        return redirect(reverse('home'))


    def guardar_tipo_empleado(self,form):
        empleador = Empleador(
            usuario_id = User.objects.get(username = form.cleaned_data['username']).id,
        )
        empleador.save()
        
class InicioSesionView(LoginView):
    template_name = 'inicio_sesion.html'
    authentication_form = InicioSesionForm #authentication_form es uno personalizado que tiene que heredad de AuthenticationForm
    success_url = '/'

class CerrarSesionView(LogoutView):

    next_page = '/inicio_sesion/' #next_page es la url a donde te lleva luego de cerrar sesion

class InicioEmpleadorView(TemplateView):
    template_name = 'home_empleador.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CargaEmpleoForm
        return context

class InicioEmpleadoView(TemplateView):
    template_name = 'home_empleado.html'

    def get_context_data(self,**kwargs):
        context = super(InicioEmpleadoView,self).get_context_data(**kwargs)
        context['tipos_empleos'] = Tipo_Empleo.objects.all()
        empleado = Usuario.objects.get_subclass(usuario_id = self.request.session['_auth_user_id'])
        context['empleado'] = empleado
        empleos_interes = empleos_interesados(Usuario.objects.get_subclass(usuario_id = self.request.session['_auth_user_id']))
        context['empleos_interes'] = empleos_interes[:4]
        context['solicitudes'] = SolicitudEmpleo.objects.filter(empleado = empleado)
        return context

class ListadoEmpleosEmpleadorView(ListView):
    template_name = 'listado_empleos_empleador.html'  
    paginate_by = 4
    def get_context_data(self, **kwargs):
        context = super(ListadoEmpleosEmpleadorView,self).get_context_data(**kwargs)
        context['form'] = CargaEmpleoForm
        return context

    def get_queryset(self):
        empleador_id = Usuario.objects.get(usuario_id = self.request.session['_auth_user_id']).id
        print(empleador_id)
        return Empleo.objects.filter(empleador_id = empleador_id).order_by('-fecha_publicacion')

class BorrarEmpleoView(DeleteView):
    model = Empleo
    success_url = '/listado_empleos_empleador/'

class ActualizarEmpleoView(UpdateView):
    model = Empleo
    fields = ['tipo_empleo','idioma','descripcion','anios_experiencia']
    template_name = 'actualizar_empleo.html'
    success_url = '/listado_empleos_empleador/'

class ActualizarDatosEmpleadoView(FormView):
    form_class = ActualizarEmpleadoForm
    template_name = 'actualizar_datos_empleado.html'
    
    def __valores_iniciales(self,empleado,user):
        """
        Devuelve los valores iniciales del formulario
        :param empleado: Empleado
        :param user: User
        :return: Dictionary
        """
        return {
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'email': user.email,
            'cv': empleado.cv,
            'anios_experiencia': empleado.anios_experiencia,
            'idioma': [idioma.id for idioma in empleado.idioma.all()],
            'tipos_empleos_interes': [tipo_empleo.id for tipo_empleo in empleado.tipos_empleos_interes.all()]
        }
        
    def usuarios(self):
        """
        Devuelve los usuarios que van a usarse
        """
        id_empleado = self.kwargs['pk']
        empleado = Empleado.objects.get(id = id_empleado)
        usuario = Usuario.objects.get(usuario_id = empleado.usuario_id)
        user = User.objects.get(id = usuario.usuario_id)     
        
        return {
            'empleado': empleado,
            'usuario': usuario,
            'user': user
        }

    def get_initial(self):
        form_tipos_usuarios = self.usuarios()
        return self.__valores_iniciales(form_tipos_usuarios['empleado'],form_tipos_usuarios['user'])   

    def form_valid(self,form):
        form_tipos_usuarios = self.usuarios()
        user = form_tipos_usuarios['user']
        user.email = form.cleaned_data['email']
        user.username = form.cleaned_data['username']
        user.last_name = form.cleaned_data['last_name']
        user.first_name = form.cleaned_data['first_name']
        user.save()
        
        empleado = form_tipos_usuarios['empleado']
        print(empleado)
        empleado.cv = form.cleaned_data['cv']
        empleado.anios_experiencia = form.cleaned_data['anios_experiencia']
        empleado.save()

        idiomas = form.cleaned_data['idioma']
        #Permite borrar todas las tuplas de la relacion many to many
        "Borramos las relaciones pre-existentes por si borra alguna idioma"
        idiomas_empleado = empleado.idioma.all()

        for idioma in idiomas_empleado:
            empleado.idioma.remove(idioma)
        
        "Cargamos las nuevas opciones de idiomas"

        for idioma in idiomas:
            empleado.idioma.add(idioma)
        
        "Borramos las relaciones pre-existentes por si borro algun tipo de empleo"
        tipos_empleos_empleado = empleado.tipos_empleos_interes.all()
        tipos_empleos = form.cleaned_data['tipos_empleos_interes']
        
        for empleo_empleado in tipos_empleos_empleado:
            empleado.tipos_empleos_interes.remove(empleo_empleado)

        "Cargamos los tipos de empleos"
        for tipo_empleo in tipos_empleos:
            empleado.tipos_empleos_interes.add(tipo_empleo)

        return redirect('/')

class ListadoAplicantesView(ListView):
    template_name = 'listado_aplicantes.html'
    paginate_by = 3

    def get_queryset(self):
        empleo_id = self.kwargs['empleo_id']
        return SolicitudEmpleo.objects.filter(empleo_id = empleo_id,aceptado = False)

class ListadoEmpleosAplicadosView(ListView):        
    template_name = 'listado_empleos_aplicados.html'
    paginate_by = 4

    def solicitudes(self,id_usuario):
        empleado = Usuario.objects.get_subclass(usuario_id = id_usuario)
        solicitudes = SolicitudEmpleo.objects.filter(empleado = empleado)
        print(solicitudes)
        return solicitudes

    def get_context_data(self, **kwargs):
        context = super(ListadoEmpleosAplicadosView,self).get_context_data(**kwargs)
        id_usuario = self.request.session['_auth_user_id']
        solicitudes = self.solicitudes(id_usuario)
        empleado = Usuario.objects.get_subclass(usuario_id = self.request.session['_auth_user_id'])
        context['empleado'] = empleado
        context['solicitudes_empleo'] = solicitudes
        context['tipos_empleos'] = Tipo_Empleo.objects.all()
        return context

    def get_queryset(self):
        id_usuario = self.request.session['_auth_user_id']
        solicitudes = self.solicitudes(id_usuario)
        empleos = Empleo.objects.filter(id__in = solicitudes.values('empleo_id'))  
        return empleos