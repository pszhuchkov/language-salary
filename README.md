## Сравниваем вакансии программистов
### О программе
Скрипт получает информацию о среднем уровне зарплат программистов, используя API [HeadHunter](https://hh.ru/) и [SuperJob](https://www.superjob.ru).
Полученная информация обрабатывается и выводится в терминал в виде сравнительной таблицы.
По умолчанию информация запрашивается для города Москвы и следующего списка языков
программирования (наиболее популярных): *JavaScript*, *Java*, *Python*, *Ruby*,
*PHP*, *C++*, *C#*, *C*, *Go*, *Scala*.  
[API HeadHunter](https://dev.hh.ru/)  
[API SuperJob](https://api.superjob.ru/)
### Как использовать
1. Для использования API SuperJob необходимо [зарегистрировать приложение](https://api.superjob.ru/)
   и получить секретный ключ. Для использования API HeadHunter регистрация не требуется.  
2. В директории с файлом `main.py` создать файл `.env`, который должен содержать
   переменную `SUPERJOB_KEY`:`SUPERJOB_KEY=your_secret_key`  
   *Пример*: 
   ```
   SUPERJOB_KEY=v3.r.127490355.e05a1bdce643ecca0cad495d01bbf3e60935bd19.c4c514a7d0ec3c09c9e82e946131fbd35ce0e857
   ```  
3. Python3 должен быть уже установлен. Использовать pip (или pip3, если есть конфликт с Python2) для установки зависимостей:  
```console
pip install -r requirements.txt
```  
4. Запустить скрипт:  
```console
python main.py
```
### Аргументы
По умолчанию (без указания аргументов) информация запрашивается для города Москвы.
Для выбора города, по которому необходимо собрать информацию о зарплатах, требуется
использовать следующие аргументы:  

`-hh`|`--hh_area_id` - идентификатор города API HeadHunter ([справочник](https://api.hh.ru/areas))  
`-sj`|`--sj_area_id` - идентификатор города API SuperJob ([справочник](https://api.superjob.ru/2.0/towns/))    

*Запрос информации для Москвы:*  
```console
python main.py
```
```console
python main.py -hh 1 -sj 4
```  
*Запрос информации для Новосибирска:*  
```console
python main.py -hh 4 -sj 13
``` 

### Цель проекта
Код написан в образовательных целях на онлайн-курсе для веб-разработчиков [dvmn.org](https://dvmn.org/).
