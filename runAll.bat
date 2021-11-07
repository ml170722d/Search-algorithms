@echo off

set agents=Aki Jocke Draza Bole
set mapId=0 1 2 3 4

for %%a in (%agents%) do (
    for %%b in (%mapId%) do (
        python "./main.py" "./maps/map%%b.txt" "%%a"
    )
)