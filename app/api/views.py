import json
import re
import uuid
from django.http import JsonResponse
from django.shortcuts import render
from .models import Person


# Регулярное выражение для проверки на валидность Id объектов
ID_MATCH = r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$'


def about(request):
    """ Функция представления отображает страницу с информацией."""

    return render(request, 'api/about.html')


def compare(request):
    """Функция представления обрабатывает запрос GET по адресу
    api/v1/persons/compare/. Производится сравнение векторов двух объектов."""

    if request.method == 'GET':
        # Id объектов для сравнения проверяются на валидность
        obj_id1 = request.GET.get('Id1')
        is_valid1 = re.match(ID_MATCH, obj_id1)
        obj_id2 = request.GET.get('Id2')
        is_valid2 = re.match(ID_MATCH, obj_id2)
        if not is_valid1 and not is_valid2:
            # Невалидный Id
            return JsonResponse({}, status=400)
        try:
            obj1 = Person.objects.get(uuid4=uuid.UUID(obj_id1))
            obj2 = Person.objects.get(uuid4=uuid.UUID(obj_id2))
        except Person.DoesNotExist:
            # В базе данных нет объекта с указанным Id
            return JsonResponse({}, status=204)
        # В базе данных есть объекты для сравнения
        if obj1.vector and obj2.vector:
            from .image import get_euclid
            distance = get_euclid(obj1.vector, obj2.vector)
            return JsonResponse({'Euclid': distance}, status=200)
        return JsonResponse({}, status=204)
    return JsonResponse({}, status=400)


def index(request):
    """Функция представления отображает главную страницу."""

    return render(request, 'api/index.html')


def get_info(request, obj_id):
    """Функция представления обрабатывает запросы GET и DELETE по адресу
    api/v1/persons/<obj_id>/.
    @param obj_id: Id объекта, информацию о котором нужно получить."""

    # Id проверяется на валидность
    is_valid = re.match(ID_MATCH, obj_id)
    if not is_valid:
        # Невалидный Id
        return JsonResponse({}, status=400)
    if request.method == 'GET':
        # Запрос на получение информации
        try:
            obj = Person.objects.get(uuid4=uuid.UUID(obj_id))
        except Person.DoesNotExist:
            # В базе данных нет объекта с указанным Id
            return JsonResponse({}, status=204)
        # В базе данных есть объект
        response = {'first_name': obj.first_name,
                    'last_name': obj.last_name}
        response['vector'] = True if obj.vector else False
        return JsonResponse(response, status=200)
    if request.method == 'DELETE':
        # Запрос на удаление объекта
        try:
            obj = Person.objects.get(uuid4=uuid.UUID(obj_id))
        except Person.DoesNotExist:
            # В базе данных нет объекта с указанным Id
            return JsonResponse({}, status=204)
        # В базе данных есть объект для удаления
        obj.delete()
        return JsonResponse({}, status=200)
    return JsonResponse({}, status=400)


def post_get_put(request):
    """Функция представления обрабатывает запросы POST, GET, PUT по адресу
    api/v1/persons/."""

    if request.method == 'POST':
        # Запрос на создание нового объекта
        data = json.loads(request.body.decode('utf-8'))
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        if first_name and last_name:
            uuid4 = uuid.uuid4()
            while Person.objects.filter(uuid4=uuid4):
                uuid4 = uuid.uuid4()
            new_obj = Person(
                uuid4=uuid4, first_name=first_name, last_name=last_name)
            new_obj.save()
            return JsonResponse({'Id': uuid4}, status=201)
        else:
            return JsonResponse({}, status=400)
    if request.method == 'GET':
        # Запрос на получение Id всех объектов
        ids = []
        for person in Person.objects.all():
            ids.append(person.uuid4)
        return JsonResponse({'Id': ids}, status=200)
    if request.method == 'PUT':
        # Запрос на добавление вектора объекта
        put, files = request.parse_file_upload(request.META, request)
        obj_id = put['obj_id']
        # Id проверяется на валидность
        is_valid = re.match(
            r'^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-'
            r'[0-9a-fA-F]{12}$', obj_id)
        if not is_valid:
            # Невалидный Id
            return JsonResponse({}, status=400)
        # Переданный Id валиден
        try:
            obj = Person.objects.get(uuid4=uuid.UUID(obj_id))
        except Person.DoesNotExist:
            # В базе данных нет объекта с указанным Id
            return JsonResponse({}, status=204)
        # Обрабатываем изображение
        from .image import process_image
        vector = process_image(files['file'].file)
        obj.vector = vector
        obj.save()
        return JsonResponse({}, status=202)
    return JsonResponse({}, 400)
