from django.shortcuts import render
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.exceptions import ValidationError
from .models import Cursos, Matriculas, Instructor


def home(request):
    return render(request, 'home.html')

def indexInstructor(request):
    instructores = Instructor.objects.all()
    return render(request, 'indexInstructor.html', {'instructores': instructores})

def nuevoInstructor(request):
    return render(request, 'nuevoInstructor.html')

def guardarInstructor(request):
    cedula = request.POST.get('cedula', '').strip()
    apellidos = request.POST.get('apellidos', '').strip()
    nombres = request.POST.get('nombres', '').strip()
    titulo = request.POST.get('titulo', '').strip()
    foto = request.FILES.get('foto')

    # Validaciones del lado del servidor
    if not cedula or not cedula.isdigit() or len(cedula) != 10:
        messages.error(request, 'La cédula debe tener 10 dígitos')
        return redirect('/nuevoInstructor')
    
    if Instructor.objects.filter(cedula=cedula).exists():
        messages.error(request, 'La cédula ya existe en el sistema')
        return redirect('/nuevoInstructor')
    
    if not apellidos or not apellidos.replace(' ', '').isalpha():
        messages.error(request, 'Los apellidos solo deben contener letras')
        return redirect('/nuevoInstructor')
    
    if not nombres or not nombres.replace(' ', '').isalpha():
        messages.error(request, 'Los nombres solo deben contener letras')
        return redirect('/nuevoInstructor')
    
    if not titulo:
        messages.error(request, 'El título es requerido')
        return redirect('/nuevoInstructor')

    Instructor.objects.create(
        cedula=cedula,
        apellidos=apellidos,
        nombres=nombres,
        titulo=titulo,
        foto=foto
    )

    messages.success(request, 'Instructor registrado correctamente')
    return redirect('/indexInstructor')

def eliminarInstructor(request, id):
    instructorEliminar = Instructor.objects.get(id=id)
    instructorEliminar.delete()

    messages.success(request, 'Instructor eliminado correctamente')
    return redirect('/indexInstructor')

def editarInstructor(request, id):
    instructorEditar = Instructor.objects.get(id=id)
    return render(request, 'editarInstructor.html', {'Instructor': instructorEditar})

def actualizarInstructor(request):
    id = request.POST.get('id')
    cedula = request.POST.get('cedula', '').strip()
    apellidos = request.POST.get('apellidos', '').strip()
    nombres = request.POST.get('nombres', '').strip()
    titulo = request.POST.get('titulo', '').strip()

    # Validaciones del lado del servidor
    if not cedula or not cedula.isdigit() or len(cedula) != 10:
        messages.error(request, 'La cédula debe tener 10 dígitos')
        return redirect(f'/editarInstructor/{id}/')
    
    instructorEditar = Instructor.objects.get(id=id)
    
    # Verificar si la cédula ya existe en otro instructor
    if Instructor.objects.filter(cedula=cedula).exclude(id=id).exists():
        messages.error(request, 'La cédula ya existe en el sistema')
        return redirect(f'/editarInstructor/{id}/')
    
    if not apellidos or not apellidos.replace(' ', '').isalpha():
        messages.error(request, 'Los apellidos solo deben contener letras')
        return redirect(f'/editarInstructor/{id}/')
    
    if not nombres or not nombres.replace(' ', '').isalpha():
        messages.error(request, 'Los nombres solo deben contener letras')
        return redirect(f'/editarInstructor/{id}/')
    
    if not titulo:
        messages.error(request, 'El título es requerido')
        return redirect(f'/editarInstructor/{id}/')

    instructorEditar.cedula = cedula
    instructorEditar.apellidos = apellidos
    instructorEditar.nombres = nombres
    instructorEditar.titulo = titulo

    if 'foto' in request.FILES:
        instructorEditar.foto = request.FILES['foto']

    instructorEditar.save()

    messages.success(request, 'Instructor actualizado correctamente')
    return redirect('/indexInstructor')


def indexCurso(request):
    listadoCursos = Cursos.objects.select_related('instructor').all()
    return render(request, 'indexCurso.html', {'cursos': listadoCursos})

def generar_pdf_cursos(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="reporte_matriculas_por_curso.pdf"'

    p = canvas.Canvas(response, pagesize=letter)

    # Título
    p.setFont("Helvetica-Bold", 18)
    p.drawString(100, 750, "REPORTE DE MATRÍCULAS POR CURSO")
    p.line(50, 740, 550, 740)

    # Encabezado
    p.setFont("Helvetica-Bold", 12)
    y = 720
    p.drawString(50, y, "Nombre Curso")
    p.drawString(200, y, "Área")
    p.drawString(300, y, "Cupo Máx")
    p.drawString(380, y, "Matriculados")
    p.drawString(480, y, "Cupos Disponibles")

    y -= 20
    p.setFont("Helvetica", 11)

    cursos = Cursos.objects.all()
    for curso in cursos:
        matriculados = curso.matriculas.count()  # cantidad de estudiantes matriculados
        cupos_disponibles = curso.Cupo  # cupos actuales

        p.drawString(50, y, curso.nombre)
        p.drawString(200, y, curso.Area)
        p.drawString(300, y, str(curso.Cupo + matriculados))  # cupo máximo original
        p.drawString(380, y, str(matriculados))
        p.drawString(480, y, str(cupos_disponibles))

        y -= 20
        if y < 50:  # nueva página si se acaba el espacio
            p.showPage()
            y = 750

    p.showPage()
    p.save()

    return response

def nuevoCurso(request):
    # Trae instructores que NO tengan cursos asignados
    instructores_libres = Instructor.objects.filter(cursos__isnull=True)
    
    return render(request, 'nuevoCurso.html', {
        'instructores': instructores_libres
    })

def guardarCursos(request):
    instructor_id = request.POST.get('instructor')
    nombre = request.POST.get('nombre', '').strip()
    Area = request.POST.get('Area', '').strip()
    Duracion = request.POST.get('Duracion', '').strip()
    Cupo = request.POST.get('Cupo', '').strip()
    estado = request.POST.get('estado', '').strip()

    # Validaciones
    if not nombre or not nombre.replace(' ', '').isalpha():
        messages.error(request, 'El nombre solo debe contener letras')
        return redirect('/nuevoCurso')
    
    if not Area:
        messages.error(request, 'Seleccione un área')
        return redirect('/nuevoCurso')
    
    if not Duracion or not Duracion.isdigit() or int(Duracion) < 1 or int(Duracion) > 200:
        messages.error(request, 'La duración debe ser entre 1 y 200 horas')
        return redirect('/nuevoCurso')
    
    if not Cupo or not Cupo.isdigit() or int(Cupo) < 1 or int(Cupo) > 20:
        messages.error(request, 'El cupo debe ser entre 1 y 20')
        return redirect('/nuevoCurso')
    
    if not estado:
        messages.error(request, 'Seleccione el estado')
        return redirect('/nuevoCurso')

    Cursos.objects.create(
        nombre=nombre,
        Area=Area,
        Duracion=Duracion,
        Cupo=int(Cupo),
        estado=estado,
        instructor=Instructor.objects.get(id=instructor_id)
    )

    messages.success(request, 'Curso registrado correctamente')
    return redirect('/indexCurso')


def eliminarCurso(request, id):
    CursosEliminar = Cursos.objects.get(id=id)
    CursosEliminar.delete()
    messages.success(request, 'Curso eliminado correctamente')
    return redirect('/indexCurso')

def editarCurso(request, id):
    cursoEditar = Cursos.objects.get(id=id)
    instructores = Instructor.objects.all()
    return render(request, 'editarCurso.html', {
        'Cursos': cursoEditar,
        'instructores': instructores
    })

def actualizarCurso(request):
    id = request.POST.get('id')
    nombre = request.POST.get('nombre', '').strip()
    Area = request.POST.get('Area', '').strip()
    Duracion = request.POST.get('Duracion', '').strip()
    Cupo = request.POST.get('Cupo', '').strip()
    estado = request.POST.get('estado', '').strip()
    instructor_id = request.POST.get('instructor')

    # Validaciones
    if not nombre or not nombre.replace(' ', '').isalpha():
        messages.error(request, 'El nombre solo debe contener letras')
        return redirect(f'/editarCurso/{id}')
    
    if not Area:
        messages.error(request, 'Seleccione un área')
        return redirect(f'/editarCurso/{id}')
    
    if not Duracion or not Duracion.isdigit() or int(Duracion) < 1 or int(Duracion) > 200:
        messages.error(request, 'La duración debe ser entre 1 y 200 horas')
        return redirect(f'/editarCurso/{id}')
    
    if not Cupo or not Cupo.isdigit() or int(Cupo) < 1 or int(Cupo) > 20:
        messages.error(request, 'El cupo debe ser entre 1 y 20')
        return redirect(f'/editarCurso/{id}')
    
    if not estado:
        messages.error(request, 'Seleccione el estado')
        return redirect(f'/editarCurso/{id}')

    cursoEditar = Cursos.objects.get(id=id)
    cursoEditar.nombre = nombre
    cursoEditar.Area = Area
    cursoEditar.Duracion = Duracion
    cursoEditar.Cupo = int(Cupo)
    cursoEditar.estado = estado
    cursoEditar.instructor = Instructor.objects.get(id=instructor_id)

    cursoEditar.save()

    messages.success(request, 'Curso actualizado correctamente')
    return redirect('/indexCurso')

def indexMatricula(request):
    listadoMatriculas = Matriculas.objects.all()
    return render(request, 'indexMatricula.html', {'matriculas': listadoMatriculas})


def nuevaMatricula(request):
    cursos_disponibles = Cursos.objects.filter(estado='Activo', Cupo__gt=0)
    
    if not cursos_disponibles.exists():
        messages.warning(request, "No hay cursos disponibles para matrícula")
    
    return render(request, 'nuevaMatricula.html', {'cursos': cursos_disponibles})


def guardarMatriculas(request):
    try:
        Nombre = request.POST.get('Nombre', '').strip()
        identidad = request.POST.get('identidad', '').strip()
        Curso_Matricula_id = request.POST.get('Curso_Matricula')

        # Validaciones
        if not Nombre or not Nombre.replace(' ', '').isalpha():
            messages.error(request, 'El nombre solo debe contener letras')
            return redirect('/nuevaMatricula')
        
        if not identidad or not identidad.isdigit() or len(identidad) != 10:
            messages.error(request, 'La cédula debe tener 10 dígitos')
            return redirect('/nuevaMatricula')
        
        if not Curso_Matricula_id:
            messages.error(request, 'Seleccione un curso')
            return redirect('/nuevaMatricula')

        curso = Cursos.objects.get(id=Curso_Matricula_id)

        # VALIDAR SI YA ESTÁ MATRICULADO
        if Matriculas.objects.filter(
            identidad=identidad,
            Curso_Matricula=curso
        ).exists():
            messages.error(
                request,
                "El estudiante ya está matriculado en este curso"
            )
            return redirect('/nuevaMatricula')

        # Validar cupo
        if curso.Cupo <= 0:
            messages.error(request, "Este curso ya no tiene cupo disponible")
            return redirect('/nuevaMatricula')

        # Crear matrícula
        matricula = Matriculas(
            Nombre=Nombre,
            identidad=identidad,
            Curso_Matricula=curso
        )
        matricula.full_clean()
        matricula.save()

        # Restar cupo
        curso.Cupo -= 1
        if curso.Cupo == 0:
            curso.estado = 'Inactivo'
        curso.save()

        messages.success(request, "Matrícula registrada correctamente")
        return redirect('/indexMatricula')

    except ValueError as e:
        messages.error(request, "Datos inválidos")
        return redirect('/nuevaMatricula')
    except Exception as e:
        messages.error(request, f"Error: {str(e)}")
        return redirect('/nuevaMatricula')



def eliminarMatricula(request, id):
    matriculaEliminar = Matriculas.objects.get(id=id)

    Curso_Matricula = matriculaEliminar.Curso_Matricula
    Curso_Matricula.Cupo += 1
    Curso_Matricula.estado = 'Activo'
    Curso_Matricula.save()

    matriculaEliminar.delete()

    messages.success(request, 'Matricula eliminada correctamente')
    return redirect('/indexMatricula')


def editarMatricula(request, id):
    matriculaEditar = Matriculas.objects.get(id=id)
    cursos = Cursos.objects.filter(estado='Activo') | Cursos.objects.filter(id=matriculaEditar.Curso_Matricula.id)

    return render(request, 'editarMatricula.html', {
        'Matriculas': matriculaEditar,
        'cursos': cursos
    })

def actualizarMatricula(request):
    id = request.POST.get('id')
    Nombre = request.POST.get('Nombre', '').strip()
    identidad = request.POST.get('identidad', '').strip()
    fecha_Matricula = request.POST.get('fecha_Matricula', '').strip()
    Curso_Matricula_id = request.POST.get('Curso_Matricula')

    # Validaciones
    if not Nombre or not Nombre.replace(' ', '').isalpha():
        messages.error(request, 'El nombre solo debe contener letras')
        return redirect(f'/editarMatricula/{id}')
    
    if not identidad or not identidad.isdigit() or len(identidad) != 10:
        messages.error(request, 'La cédula debe tener 10 dígitos')
        return redirect(f'/editarMatricula/{id}')
    
    if not fecha_Matricula:
        messages.error(request, 'La fecha de matrícula es requerida')
        return redirect(f'/editarMatricula/{id}')
    
    if not Curso_Matricula_id:
        messages.error(request, 'Seleccione un curso')
        return redirect(f'/editarMatricula/{id}')

    matriculaEditar = Matriculas.objects.get(id=id)
    CursoNuevo = Cursos.objects.get(id=Curso_Matricula_id)

    # Actualizar cupos si cambia de curso
    if matriculaEditar.Curso_Matricula.id != CursoNuevo.id:
        matriculaAnterior = matriculaEditar.Curso_Matricula
        matriculaAnterior.Cupo += 1
        matriculaAnterior.estado = 'Activo'
        matriculaAnterior.save()

        CursoNuevo.Cupo -= 1
        if CursoNuevo.Cupo == 0:
            CursoNuevo.estado = 'Inactivo'
        CursoNuevo.save()

    matriculaEditar.Nombre = Nombre
    matriculaEditar.identidad = identidad
    matriculaEditar.fecha_Matricula = fecha_Matricula
    matriculaEditar.Curso_Matricula = CursoNuevo
    matriculaEditar.save()

    messages.success(request, 'Matricula actualizada correctamente')
    return redirect('/indexMatricula')


