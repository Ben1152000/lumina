python3 assembler.py $1 |
curl -X POST http://pi.bdarnell.com:8010/programs/test \
    -H 'Content-Type: application/octet-stream' \
    --data-binary '@-' && \
curl -X POST http://pi.bdarnell.com:8010/execute/test