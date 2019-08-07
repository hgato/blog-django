# Django Blog

This is a test project

## Dev deployment

1. Make `.env` file in `docker` folder:
    ```
    POSTGRES_USER=admin_user
    POSTGRES_PASSWORD=admin_user_password
    POSTGRES_DB=blog_db
    BACKEND_DEBUG=True
    DJANGO_JWT_SECRET=some_secret_code
    ```
2. Execute `docker/logstash/conf.d/config_generator.py`
3. Execute `sudo sysctl -w vm.max_map_count=524288` to enable docker Elasticsearch
4. Change directory to docker and execute `docker-compose up`
5. From the same folder execute `docker-compose exec backend bash` and then `python manage.py runserver 0.0.0.0:8000` from container
6. From the same folder execute `docker-compose exec node bash` and then `yarn start` from container
7. Site is accessible from `localhost`
