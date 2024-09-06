# SceneSwitcher webapplication

## Getting started

### Build a Docker file

```
docker-compose build
```

### To start project, run:

```
docker-compose up
```

### To stop project, run:

```
docker-compose down
```

## Development Guide

### Load Initial Admin

#### 1.

```
docker-compose run --rm app sh -c "python manage.py superuser_init"
```

### Username

```
admin2

```

### Password

```
admin2

```
