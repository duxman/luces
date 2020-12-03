@echo off

echo convertir %1 en converted_%1 con %2 db
sox.exe  %1  -b 8 --norm=%2 -e unsigned-integer converted_%1  channels 1 rate 8k 

