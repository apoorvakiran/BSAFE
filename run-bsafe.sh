
export AWS_ACCESS_KEY_ID=AKIA6LZBSJYHWUQEACWN
export AWS_SECRET_ACCESS_KEY=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
export AWS_DEFAULT_REGION=us-east-1

#export INPUT_S3_PATH=s3://mindy-iteratelabs-phone-data/NEWFACTORY/raw/2021/12/19/C0:D7:06:E5:78:5F/C0_D7_06_E5_78_5F_20211209_67
# export INPUT_S3_PATH=s3://mindy-iteratelabs-phone-data/NEWFACTORY/raw/2021/12/19/C0:D7:06:E5:78:5F/56_22_5B_23_5E_B6.crash
export OUTPUT_S3=mindy-iteratelabs-bsafe-data
export GIT_PYTHON_REFRESH=quiet
export INFINITY_GAUNTLET_PASSWORD=EZ4x0tr7a+._pRyA
export INFINITY_GAUNTLET_URL=https://api.mindy.iteratelabs.co
export INFINITY_GAUNTLET_USERNAME=e2e_test@user.com

file=$INPUT_S3_PATH
set
function urldecode() { : "${*//+/ }"; echo -e "${_//%/\\x}"; }
file=`urldecode $file`

echo "______________________________________"
echo "run pipenv run python3 run_v2.py $file "
echo "______________________________________"
pipenv run python3 run_v2.py $file


