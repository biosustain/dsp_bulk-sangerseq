# script to start a docker container for testing
docker run -v /Users/sebschu/Documents/senDS_cfb/code/dsp_bulk-sangerseq/docker_tests/input_data:/home/input_data -v /Users/sebschu/Documents/senDS_cfb/code/dsp_bulk-sangerseq/docker_tests/output:/home/output --name assemble_test -it --platform linux/amd64 geargenomics/tracy:latest
