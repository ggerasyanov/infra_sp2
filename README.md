# Тренировочный проект infra_sp2

### Как развернуть проект:
Клонируем репозеторий с GitHub:
```
git clone https://github.com/ggerasyanov/infra_sp2.git
```
Перейти в репозиторий с файлом docker-compose.yaml:
```
cs .../infra_sp2/infra/
```
Собрать контейнеры для заупска::
```
# Запускать в папке с файлом docker-compose.yml
docker-compose up
docker-compose up -d # в фоновом режиме
```
Проект запустится в трёх контейнерах: db (postgres:13.0-alpine), web (backend), nginx (nginx:1.21.3-alpine).

### Описание:
Данный проект был создан в целях тренировки контейнеризации проектов. В данном случае в контейнер упаковывается проект api_yamdb (https://github.com/ggerasyanov/api_yamdb).
