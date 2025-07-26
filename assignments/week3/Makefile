include .env

build:
	docker-compose build

up:
	docker-compose up -d 

down:
	docker-compose down

restart:
	make down && make up

to_psql:
	docker exec -ti de_psql psql -U $(POSTGRES_USER) -d $(POSTGRES_DB)

to_mysql:
	docker exec -it de_mysql mysql --local-infile=1 -u$(MYSQL_USER) -p$(MYSQL_PASSWORD) $(MYSQL_DATABASE)

to_mysql_root:
	docker exec -it de_mysql mysql -u root -p$(MYSQL_ROOT_PASSWORD) $(MYSQL_DATABASE)