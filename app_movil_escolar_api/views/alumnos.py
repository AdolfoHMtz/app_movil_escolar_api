from django.db import transaction
from rest_framework import permissions, generics, status
from rest_framework.response import Response
from django.contrib.auth.models import Group, User

from app_movil_escolar_api.serializers import UserSerializer, AlumnoSerializer
from app_movil_escolar_api.models import Alumnos


class AlumnoAll(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        user = request.user
        # Obtener todos los alumnos
        alumnos = Alumnos.objects.all()
        serializer = AlumnoSerializer(alumnos, many=True)
        return Response(serializer.data, 200)


class AlumnoView(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)
    # Registrar nuevo alumno
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        # Serializamos los datos del alumno para volverlo de nuevo JSON
        user = UserSerializer(data=request.data)

        if user.is_valid():
            # Grab user data
            role = request.data['rol']
            first_name = request.data['first_name']
            last_name = request.data['last_name']
            email = request.data['email']
            password = request.data['password']
            # Valida si existe el usuario o bien el email registrado
            existing_user = User.objects.filter(email=email).first()

            if existing_user:
                return Response({"message": "Username " + email + ", is already taken"}, 400)

            user = User.objects.create(
                username=email,
                email=email,
                first_name=first_name,
                last_name=last_name,
                is_active=1
            )

            user.save()
            # Cifrar la contraseña
            user.set_password(password)
            user.save()

            group, created = Group.objects.get_or_create(name=role)
            group.user_set.add(user)
            user.save()

            # Almacenar los datos adicionales del alumno
            alumno = Alumnos.objects.create(
                user=user,
                matricula=request.data.get("matricula", ""),
                telefono=request.data.get("telefono", ""),
                rfc=request.data.get("rfc", "").upper(),
                curp=request.data.get("curp", "").upper(),
                edad=request.data.get("edad", None),
                ocupacion=request.data.get("ocupacion", ""),
                fecha_nacimiento=request.data.get("fecha_nacimiento", None)
            )
            alumno.save()

            return Response({"alumno_created_id": alumno.id}, 201)

        return Response(user.errors, status=status.HTTP_400_BAD_REQUEST)
