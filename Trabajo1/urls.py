"""Trabajo1 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls        import url
from django.urls             import path
from django.contrib          import admin
from Trabajo1                import views
from django.conf.urls.static import static
from django.conf             import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^$',views.InicioView.as_view(),name = 'home'),
    path('home_empleado/',views.InicioEmpleadoView.as_view(),name = 'home_empleado'),
    path('home_empleador/',views.InicioEmpleadorView.as_view(),name = 'home_empleador'),
    path('registro_empleado/',views.RegistroEmpleadoView.as_view(),name = 'registro_empleado'),
    path('registro_empleador/',views.RegistroEmpleadorView.as_view(),name = 'registro_empleador'),
    path('listado_empleos_empleador/',views.ListadoEmpleosEmpleadorView.as_view(),name = 'listado_empleos_empleador'),
    path('cargar_empleo/',views.cargar_empleo,name = 'carga_empleor'),
    path('busqueda_empleo/',views.Busqueda_Empleo.as_view(),name = 'busqueda_empleo'),
    path('inicio_sesion/',views.InicioSesionView.as_view(),name = 'inicio_sesion'),
    path('cierre_sesion/',views.CerrarSesionView.as_view(),name = 'cierre_sesion'),
    path('borrar_empleo/<pk>/',views.BorrarEmpleoView.as_view(),name = 'borrar_empleo'),
    path('actualizar_empleo/<pk>/',views.ActualizarEmpleoView.as_view(),name='actualizar_empleo'),
    path('actualizar_datos_empleado/<pk>/',views.ActualizarDatosEmpleadoView.as_view(),name = 'actualizar_datos_empleado'),
    path('aplicar_empleo/<id_empleo>/',views.aplicar_empleo, name = 'aplicar_empleo'),
    path('listado_aplicantes/<int:empleo_id>',views.ListadoAplicantesView.as_view(), name = 'listado_aplicantes'),
    path('aceptar_entrevista/<int:id_solicitud>',views.aceptar_entrevista,name = 'aceptar_entrevista'),
    path('listado_empleos_aplicados/',views.ListadoEmpleosAplicadosView.as_view(),name = 'listado_empleos_aplicados'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)