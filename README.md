# opentix-project


`wsl`  
`cd ~`  
`git clone https://github.com/ianl20230303/opentix-project.git`  
`cd opentix-project/`  


`docker compose -f docker-compose-local.yml up -d --build mysql phpmyadmin`  


`uv sync`  
run create schema + table in file:opentix_db.sql  
run file:crawler/opentix-crawler.py


`hostname -I`  