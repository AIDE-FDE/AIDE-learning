up:
	docker-compose up -d

down:
	docker-compose down

create_table:
	docker exec de_psql psql postgres://admin:admin123@localhost:5432/brazillian_ecommerce -f /tmp/psql_schemas.sql

to_psql:
	docker exec -ti de_psql psql -U $(POSTGRES_USER) -d $(POSTGRES_DB)

dbt-build:
	dbt build --profiles-dir ./brazillian_ecom --project-dir brazillian_ecom

dbt-run:	
	dbt run --profiles-dir ./brazillian_ecom --project-dir brazillian_ecom

dbt-docs:
	dbt docs generate --profiles-dir ./brazillian_ecom --project-dir brazillian_ecom && dbt docs serve --profiles-dir ./brazillian_ecom --project-dir brazillian_ecom
