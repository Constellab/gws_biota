cd ./docs/ 
sphinx-quickstart
rm ./docs/source/conf.py
cp ./docs/templates/conf.py ./docs/source/
sphinx-apidoc -o ./source ../biota/prism
sphinx-build -b html ./source ./build