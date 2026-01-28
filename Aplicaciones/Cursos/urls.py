from django.urls import path
from . import views

urlpatterns = [
    path('', views.home), #pagina principal
    path('home/', views.home),

    path('indexInstructor/', views.indexInstructor, name='indexInstructor'),
    path('nuevoInstructor/', views.nuevoInstructor, name='nuevoInstructor'),
    path('guardarInstructor/', views.guardarInstructor, name='guardarInstructor'),
    path('editarInstructor/<int:id>/', views.editarInstructor, name='editarInstructor'),
    path('actualizarInstructor/', views.actualizarInstructor, name='actualizarInstructor'),
    path('eliminarInstructor/<int:id>/', views.eliminarInstructor, name='eliminarInstructor'),



    path('indexCurso', views.indexCurso),
    path('nuevoCurso', views.nuevoCurso),
    path('guardarCursos', views.guardarCursos),
    path('eliminarCurso/<int:id>', views.eliminarCurso),
    path('editarCurso/<int:id>', views.editarCurso),
    path('actualizarCurso', views.actualizarCurso),

    # PDF Cursos
    path('generar_pdf_cursos/', views.generar_pdf_cursos),

    path('indexMatricula', views.indexMatricula),
    path('nuevaMatricula', views.nuevaMatricula),
    path('guardarMatriculas', views.guardarMatriculas),
    path('editarMatricula/<int:id>', views.editarMatricula),
    path('actualizarMatricula', views.actualizarMatricula),
    path('eliminarMatricula/<int:id>', views.eliminarMatricula),

  

]
