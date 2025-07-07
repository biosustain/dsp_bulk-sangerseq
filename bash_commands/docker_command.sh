#this command works
docker run --name two --entrypoint /bin/sh -itd --platform linux/amd64 geargenomics/tracy:latest

#this command works and correctly mounts the data drive
docker run -v /Users/sebschu/Documents/senDS_cfb/code/tracy/data/sanger_seq:/home/data_sanger_seq --name three --entrypoint /bin/sh -itd --platform linux/amd64 geargenomics/tracy:latest

docker attach three     #to get into the container


#this command (using only -it) works: it directly opens the container without the need to attach to it; it correctly mounts the data drive
docker run -v /Users/sebschu/Documents/senDS_cfb/code/tracy/data/sanger_seq:/home/data_sanger_seq --name four --entrypoint /bin/sh -it --platform linux/amd64 geargenomics/tracy:latest

#this command (using only -it; no entrypoint argument) works: it directly opens the container without the need to attach to it; it correctly mounts the data drive
docker run -v /Users/sebschu/Documents/senDS_cfb/code/tracy/data/sanger_seq:/home/data_sanger_seq --name five -it --platform linux/amd64 geargenomics/tracy:latest













#try if this one works to create a new container (docker run creates a new container)
docker run -it --entrypoint /bin/bash geargenomics/tracy:latest

#try if this one works for already existing containers (docker exec uses an already existing container)
docker exec -it <mycontainer> sh

