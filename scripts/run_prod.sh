
#docker stop allezon-redis || true
#docker rm allezon-redis || true
#docker run --name allezon-redis -p 6778:6778  -d redis redis-server --appendonly yes --save "" --port 6778

docker build . -t allezon
docker stop allezon-backend || true
docker rm allezon-backend || true
docker run --network host --name allezon-backend -p 8080:8080 -d  allezon:latest
#  cd src || true
#  docker stop allezon-backend || true
#  uvicorn main_app:app --workers 2 --host 0.0.0.0 --port 8080 --reload