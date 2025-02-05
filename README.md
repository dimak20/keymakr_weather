# Weather API Service 🌧️

<a id="readme-top"></a>

![Django DRF Logo](logos/django-rest.jpg)
![Redis Logo](logos/redis-image.svg)
![Celery Logo](logos/celery.png)

> REST project for keymakr

This system processes weather data asynchronously for a list of cities. It accepts city names via a POST request, fetches weather data from an external API, and organizes the results by geographic region (e.g., Europe, Asia).

Key features:

Asynchronous processing using Celery and Redis.
Normalizes and corrects city names (e.g., handles typos and different languages).
Filters out invalid data (e.g., incorrect temperature values).
Saves results into region-based JSON files for further analysis.

## Run with Docker

1. Clone repository  
```shell
git clone https://github.com/dimak20/keymakr_weather.git
cd keymakr_weather
```
2. Create .env file and set up environment variables
```shell
REDIS_URL=<redis://redis:6379/1>
CELERY_BROKER_URL=<redis://redis:6379/0>
CELERY_RESULT_BACKEND=<redis://redis:6379/1>
DATABASE_ENGINE=<postgresql>
POSTGRES_PASSWORD=<postgresqlpass>
POSTGRES_USER=<postgresuser>
POSTGRES_DB=<weatherdb>
POSTGRES_HOST=<db>
POSTGRES_PORT=<5432>
PGDATA=</var/lib/postgresql/data/pgdata>
WEATHER_URL=<your-weather-url, e.g. http://api.weatherapi.com/v1/current.json>
WEATHER_API_KEY=<your-weather-api-key>
WEATHER_DATA_DIR=</weather_data>
MEDIA_HOST=<your host, e.g. http://localhost:8000>
```

3. Build and run docker containers 


```shell
docker-compose up --build
```

4. Access the API at http://localhost:8000/api/v1/


5. Monitoring
```shell
Beat scheduler: http://localhost:8000/admin/ -> tasks
Flower: http://localhost:5555
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Project configuration

Your project needs to have this structure


```plaintext
Project
├── weather_app
│   ├── __init__.py
│   └── admin.py
│   ├── apps.py
|   ├── base.py
|   ├── exceptions.py
│   ├── factories.py
|   ├── models.py
|   ├── serializers.py
|   ├── services.py
│   ├── tasks.py
│   ├── urls.py
│   ├── utils.py
│   ├── validators.py
│   └── views.py
|
├── keymakr_weather
│   ├── __init__.py
│   ├── asgi.py
│   ├── permissions.py
│   ├── celery.py
│   ├── settings.py
|   ├── wsgi.py
│   └── urls.py
│
|
├── management_utils
|   └── management
|   |  └── commands
|   |     └── wait_for_db.py
│   ├── __init__.py
│   └── admin.py
│   ├── apps.py
|   ├── models.py
│   ├── urls.py
│   └── views.py
|
|
├── weather_data
│   ├── Europe
|   |  └── task_<task_id>.json
|   |  └── ...
|   ├── Asia
│   └── ...
|   
├── logs
│   
├── logos
│   
├── templates
│
├── .dockerignore
│
├── .env
|
├── .env.sample
│
├── .gitignore
│
├── Dockerfile
│
├── manage.py
│
├── README.md
|
└── requirements.txt
```
# Endpoints

| **Endpoint**            | **Method** | **Description**                                                                                          |
|-------------------------|------------|----------------------------------------------------------------------------------------------------------|
| `/weather`              | POST       | Accepts a list of cities in JSON format, initiates asynchronous weather data processing, and returns a task ID. |
| `/tasks/<task_id>`      | GET        | Fetches the status of the task (running, completed, failed) based on the task ID.                         |
| `/results/<region>`     | GET        | Returns the weather data for cities within the specified region (e.g., Europe, Asia).                     |

# Important Notes

Due to the high number of I/O-bound operations, the endpoint that handles regions can also be implemented as a background Celery task with statuses. It won't return instantly.

The geopy library, which normalizes data, makes requests at a rate of 1 request per second in its free tier. If you use a paid API key or other libraries that allow making requests more frequently (e.g., more than once per second), and make the function a coroutine, you can achieve fully asynchronous requests and significantly improve the performance of Celery tasks. The current implementation is left as-is for demonstration purposes of Celery task states (status - running and progress).


<p align="right">(<a href="#readme-top">back to top</a>)</p>
