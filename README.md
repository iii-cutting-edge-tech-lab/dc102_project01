dc102_project

啟動web服務
$mkdir work/pic
$docker build -t .
$docker run --name flask-web -p 80:5000 flask-web
