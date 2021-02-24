# -------------------------------------------
# Please call this script as `source ./load_env.sh`
#
# Copyright Iterate Labs, Inc.
# Contact: jesper.kristensen@iteratelabs.co
# -------------------------------------------

echo
echo "********************************************************"
echo "*       Welcome to BSAFE by Iterate Labs, Inc.         *"
echo "********************************************************"
# banner generated here: http://bagill.com/ascii-sig.php
echo ".______        _______.     ___       _______  _______"
echo "|   _  \      /       |    /   \     |   ____||   ____|"
echo "|  |_)  |    |   (----\`   /  ^  \    |  |__   |  |__"
echo "|   _  <      \   \      /  /_\  \   |   __|  |   __|"
echo "|  |_)  | .----)   |    /  _____  \  |  |     |  |____"
echo "|______/  |_______/    /__/     \__\ |__|     |_______|"
echo ""

# Set up the virtual environment from the pipfile:
# (see the Pipfile and Pipfile.lock):
echo "Setting up the Python environment for BSAFE"
# pipenv update --dev
echo "[OK] Python has been set up."

# NOTE: THIS MESSES UP SOME LINE ENDINGS
# echo "Setting up the Data Storage script..."
# first_line=$(head -n 1 scripts/data_storage.py)
# if [[ $first_line == "#"* ]]
# then
# 	tail -n +2 scripts/data_storage.py > data_storage.tmp && mv
# 	data_storage.tmp scripts/data_storage.py
# fi
# echo -e "#"'!'"`which python`\n$(cat scripts/data_storage.py)" >
# scripts/data_storage.py
#pipenv run python scripts/data_storage.py > /dev/null
#echo
#echo "[OK] Data Storage set up"

echo
echo "Run python commands with \"pipenv run -m python <file to run.py>\""
echo "[ALL OK] >> BSAFE is ready for use <<"
echo

cp .env .env_backup__tmp

[[ ":$PATH:" != *":$PWD:"* ]] && PATH="$PWD:${PATH}"
[[ ":$PYTHONPATH:" != *":$PWD:"* ]] && PYTHONPATH="$PWD:${PYTHONPATH}"
echo "export PATH=$PATH" >> .env
echo "export PYTHONPATH=$PYTHONPATH" >> .env

pipenv shell

cp .env_backup__tmp .env
rm .env_backup__tmp
