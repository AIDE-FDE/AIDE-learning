# Các khái niệm trong Docker
## Docker:
Docker là một nền tảng mã nguồn mở cho phép đóng gói, vận chuyển và chạy ứng dụng trong một môi trường cách ly gọi là container.

## Container
- Là một phiên bản chạy thực tế của một image.
- Giống như một "máy tính nhỏ" bên trong máy .
- Mỗi container độc lập, nhẹ, nhanh, nhưng chia sẻ kernel với máy chủ host.

📌 Ví dụ: ta có một app Node.js. Khi chạy docker run, Docker tạo một container chứa Node.js và app của dev, hoạt động như một server riêng biệt.

## image:
- image là một bản dựng Là một bản đóng gói (snapshot) của ứng dụng – bao gồm: mã nguồn, môi trường, thư viện, công cụ, OS.
- Không thay đổi (immutable).
- Được dùng để tạo container.

📌 Ví dụ: node:18, python:3.11, nginx:latest là những image phổ biến trên Docker Hub.

## Dockerfile
- Là file cấu hình (text file) chứa tập hợp các hướng dẫn để Docker build ra một image.
- Viết bằng cú pháp riêng (giống shell script).

📌 Ví dụ
```bash
FROM node:18
WORKDIR /app
COPY . .
RUN npm install
CMD ["npm", "start"]
```

## Docker Engine
- Là thành phần cốt lõi của Docker, giúp :
    - Xây dựng image (docker build)
    - Chạy container (docker run)
    - Quản lý images, volumes, networks...

📌 Khi cài Docker Desktop hoặc Docker CLI, bạn đã cài Docker Engine.


## Docker Hub
- Là kho chứa image online miễn phí (giống như GitHub dành cho Docker).
- có thể docker pull image từ đây hoặc docker push image của mình lên.

📌 Ví dụ: docker pull nginx, docker pull mysql, docker push myname/myapp.

## Docker CLI (Command Line Interface)
- Là giao diện dòng lệnh để tương tác với Docker Engine.
- Ví dụ lệnh:
    - docker run
    - docker build
    - docker ps
    - docker stop
    - docker logs


## Layer (Lớp)
- Mỗi câu lệnh trong Dockerfile tạo ra một layer.
- Các layer được cache lại để tăng tốc build và tái sử dụng.
- Các layer xếp chồng lên nhau tạo thành một image.

📌 Ví dụ: RUN npm install là 1 layer, COPY . . là 1 layer.


## Volume
- Là cách Docker lưu trữ dữ liệu bên ngoài container.
- Dữ liệu không bị mất khi container bị xóa.
- Dùng để lưu database, upload file, log, etc.

📌 Ví dụ:
```
docker run -v my-volume:/data my-container
```

## Network
- Docker cung cấp mạng ảo riêng cho container.
- Có các loại:
    - bridge (mặc định)
    - host
    - none
    - custom (do người dùng tạo)

📌 Dùng docker network create để tạo mạng cho các container giao tiếp.


## Tag
- Là tên phiên bản của một image.
- Cú pháp: image:tag (mặc định là latest)

📌 Ví dụ:
```
docker pull node:18
docker pull ubuntu:20.04
```


## docker-compose
- Là công cụ để quản lý nhiều container cùng lúc.
- Sử dụng file docker-compose.yml để định nghĩa các service.
- Cực hữu ích khi làm project có:
    - Backend
    - Database
    - Redis
    - Nginx


📌 Ví dụ chạy:
```
docker-compose up --build
```


## Build context
- Là thư mục hiện tại chứa Dockerfile và mã nguồn khi dùng docker build.
- Docker gửi toàn bộ thư mục đó vào engine để build image.

📌 Tip: Dùng .dockerignore để bỏ qua file không cần.

## Entrypoint vs CMD
- CMD: Lệnh mặc định để chạy container.
- ENTRYPOINT: Lệnh bắt buộc chạy đầu tiên khi container khởi động.

📌 Ví dụ:
```Dockerfile
ENTRYPOINT ["python"]
CMD ["app.py"]
```
-> chạy python app.py