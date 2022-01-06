@echo off
pushd %~dp0
python ./src/main.py ./scripts/script1.lang
python ./src/main.py ./scripts/script2.lang
python ./src/main.py ./scripts/script3.lang
popd