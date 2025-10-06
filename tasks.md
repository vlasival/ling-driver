

Задание на ЛР 16/09/2025:

Изучить 5 типов запросов языка Cypher к графовой базе данных Neo4j:
CREATE: создание узлов графовой базы данных совместно с произвольным числом параметров узла
READ: получение выборки узлов в зависимости от их параметров и связей (Пример: найти все узлы :Person, которые связаны отношением :lived с узлами тега :City, где city_name = ‘Москва’)
UPDATE: обновление существующих и добавление новых параметров узла
DELETE: удаление узлов, удовлетворяющих условиям выборки
CREATE_ARC: создание связей между двумя определенными узлами
На основе данных запросов будет проведен тест.
Введение в Cypher: Введение в язык запросов Cypher / Хабр

Установить ПО Neo4j: 
Для пользователей Windows установщик находится в чате группы. 
Для пользователей Linux, MacOS – вы можете скачать десктопное приложение с офф. сайта.
Главное, чтобы версия Neo4j включала Neo4j Browser

Для практики – апробировать изученные запросы в Neo4j Browser.
Отчет на практику не нужен.



Задание на ЛР 23/09/2025:
Название лабораторной работы для отчета: Разработка драйвера для графовой базы данных Neo4j

Разработать репозиторий для работы с графовой базой данных. Репозиторий должен включать в себя следующие методы:

	def get_all_nodes() - получить все узлы графа
	def get_all_nodes_and_arcs() - получить все узлы с их связями
	def get_nodes_by_labels(labels: string[]) - получить выборку узлов по их меткам 
	def get_node_by_uri() - получить узел по uri
	
def create_node(params: {})
def create_arc(node1_uri: string, node2_uri: string)

def delete_node_by_uri()
def delete_arc_by_id()

def update_node()

def generate_random_string() - генерация строки для uri узла, при создании нового узла
def run_custom_query(query: string)  - выполнение произвольного запроса “Cypher”

def collect_node(node) => TNode
def collect_arc(arc) => TArc
TNode = {
	id: number,
	uri: string,
	description: string,
	title: string,
arcs?: TArc[]	
}

TArc = {
	id: number,
	uri: string, // arc.type
	node_uri_from: string,
	node_uri_to: string
}

Методы “collect” реализуются для удобства трансляции объекта БД в dict. В плане дизайна на будущее удобно иметь в одном месте такие функции, если трансляция расширяться будет.

По выполненной работе должен быть написан отчет. Крайний срок приема отчета: утро 22/09/2025.
Место отправки отчетов назову позже в телеграмм канале группы.

from neo4j import GraphDatabase //библиотека 

Пара функций которая может пригодиться в вашем репозитории, если нужно. Можете лучше написать.
    def transform_labels(self, labels, separator = ':'):
        if len(labels) == 0:
            return '``'
        res = ''
        for l in labels:
            i = '`{l}`'.format(l=l) + separator
            res +=i
        return res[:-1]


    def transform_props(self, props):
        if len(props) == 0:
            return ''
        data = "{"
        for p in props:
            temp = "`{p}`".format(p=p)
            temp +=':'
            temp += "{val}".format(val = json.dumps(props[p]))
            data += temp + ','
        data = data[:-1]
        data += "}"


        return data

Задание на ЛР 30/09/2025:

Лабораторная: Разработка репозитория для редактирования онтологии предметной области

Теория для лабораторной работы: Представление онтологии на графе
Задача:
	Реализовать следующие методы на основе работы предыдущей лабораторной работы:
get_ontology: получить всю онтологию
get_ontology_parent_classes: получить классы онтологии, у которых нет родителей
get_class: получить класс
get_class_parents: получить родителей класса
get_class_children: получить потомков класса
get_class_objects: получить объекты класса
update_class: обновить класс (имя и описание)
create_class: создать класс (имя, описание, родитель(?))
delete_class: удалить класс (его детей, объектов, объектов детей и т.д.)

add_class_attribue: добавить DatatypeProperty к классу (параметр)
delete_class_attribue: удалить DatatypeProperty у класса (параметр)

add_class_object_attribute(class_uri: string, attr_name: string, range_class_uri: string): добавить ObjectProperty 
delete_class_object_attribute(object_property_uri: string) // внимание на сзяви

add_class_parent(parent_uri: string, target_uri: string): присоединить родителя к классу (без создания родителя, из существующих классов)

get_object: получить объект класса
delete_object: удалить объект класса

create_object, update_object: через collect_signature
collect_signature(class_uri)




collect_signature - сбор всех (DatatypeProperty) и (ObjectProperty - range - Class) узлов у Класса

Пример структуры signature:


title: название поля класса (таблицы) Представление онтологии на графе  (в данной репрезентации это label ru/eng)

Для нашей работы label[ru, en] заменяется title: string


Старые примеры Cypher по сбору signature:



Задание на ЛР 7/10/2025

Название лабораторной работы: Разработка хранилища корпуса текстов

В рамках данной работы вам необходимо сделать хранилище текстов, с которыми вы будете работать текущий семестр.

Тексты: тексты вашей предметной области могут быть:
научные статьи
новости
проза
стихи и т.д.
Главное, что ваши тексты принадлежат одной определенной предметной области

Для создания хранилища мы используем фреймворк питона “Django”.
Скелет вашего проекта вы можете взять тут: https://github.com/sovladlisin/neo_graph_test 

Для установки всех библиотек проекта:
	pip install -r “requirements.txt”
Или вариация данной команды

Для инициализации базы данных:
	python manage.py migrate

Вам нужно:

Создать две таблицы в базе данных (пример в models.py):
Корпус: таблица, которая отображает вашу предметную область 
название
описание
жанр
Текст: таблица, которая содержит ваши тексты
название
описание
текст (поле TextField, которое будет содержать ваш текст)
corpus_id (связь с корпусом – индикатор, что данный текст принадлежит корпусу)
has_translation (связь с самим собой)
Создать endpoint (rest ссылки) для редактирования корпусов и текстов (пример в views.py) (рекомендация: предварительно сделайте репозиторий в соответствии с примером “TestRepository” для удобства и аккуратности)
create corpus
update corpus
get corpus - (gets corpus and all of its texts) (удобно если тексты собираются в collect_corpus) 
delete corpus
create text
update text
get text
delete text
Добавить результат ваших предыдущих лабораторных работ в проект (где TestRepository.py)
Добавить OntologyRepository в db.api
Добавить DriverRepository в db.api
Создать endpoint для методов в OntologyRepository (пример в views.py)


Полезные команды:

При добавлении или редактировании моделей, вам необходимо сообщить базе данных, что вы сделали какие-то добавления или редактирования.

Весь запуск методов Django осуществляется через файл manage.py

Для обновления БД вам нужно:
python manage.py makemigrations – создать файлы SQL для редактирования БД
python manage.py sqlmigrate {app_title} {migrate_version} – мигрировать созданный файл SQL, где app_title - это название приложения в django (название папки, в которой содержится файл models.py), migrate_version - это версия применяемого SQL(только цифры) - отображается в ответе команды makemigrations. Также все версии migrate хранятся в папке migrations. Например: в репозитории вы можете увидеть файл 0001_initial.py.
python manage.py migrate – применить все миграции в проект (у вас в репозитории будет 0001_initial.py, так что эта команда применит уже существующий файл)

Эти команды выполняются одна за другой в терминале директории проекта при каждом редактировании БД

Для старта сервера:
python manage.py runserver
