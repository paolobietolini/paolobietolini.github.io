.PHONY: build up down create-topic produce consume init-db q4 q5 q6 clean

build:
	docker compose build

up:
	docker compose up --build --remove-orphans -d

down:
	docker compose down --remove-orphans

clean:
	docker compose down -v --remove-orphans

create-topic:
	docker exec -it module-7-redpanda-1 rpk topic create green-trips

produce:
	uv run python src/producers/producer.py

consume:
	uv run python src/consumers/consumer.py

init-db:
	docker exec -i module-7-postgres-1 psql -U postgres -d postgres < init.sql

q4:
	docker exec -it module-7-jobmanager-1 flink run -py /opt/src/job/q4_tumbling_pickup.py

q5:
	docker exec -it module-7-jobmanager-1 flink run -py /opt/src/job/q5_session_pickup.py

q6:
	docker exec -it module-7-jobmanager-1 flink run -py /opt/src/job/q6_hourly_tips.py
