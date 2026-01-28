from django.db import models

class Instructor(models.Model):
    cedula = models.CharField(max_length=10, unique=True)
    apellidos = models.CharField(max_length=100)
    nombres = models.CharField(max_length=100)
    titulo = models.CharField(max_length=100)
    foto = models.ImageField(upload_to='instructores/', null=True, blank=True)

    def __str__(self):
        return f"{self.apellidos} {self.nombres}"

class Cursos(models.Model):
    nombre = models.CharField(max_length=100)
    Area = models.CharField(max_length=50)
    Duracion = models.CharField(max_length=20)
    Cupo = models.PositiveIntegerField()
    estado = models.CharField(
        max_length=15,
        choices=[('Activo', 'Activo'), ('Inactivo', 'Inactivo')],
        default='Activo'
    )
    
    instructor = models.ForeignKey(
    Instructor,
    on_delete=models.CASCADE,
    related_name='cursos',
    null=True,  # permite cursos sin instructor
    blank=True
)

    def __str__(self):
        return f"{self.nombre} - {self.Area}"


class Matriculas(models.Model):
    Nombre = models.CharField(max_length=150)
    identidad = models.CharField(max_length=10)
    fecha_Matricula = models.DateField(auto_now_add=True)
    Curso_Matricula = models.ForeignKey(
        Cursos,
        on_delete=models.CASCADE,
        related_name='matriculas'
    )

    def __str__(self):
        return f"{self.Nombre} - {self.Curso_Matricula.nombre}"
