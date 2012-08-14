#!/bin/bash
echo "Export the plugin to a zip with no .git folder"
if test -z "$1"
then
  echo "usage: $0 <new version>"
  echo "e.g. : $0 0.3.0"
  exit
fi

VERSION=$1

# TODO
#replace _type_ = 'alpha' or 'beta' with final

#regenerate docs
make docs

#see http://stackoverflow.com/questions/1371261/get-current-working-directory-name-in-bash-script
DIR=${PWD##*/}
OUT="/tmp/${DIR}.${1}.zip"

rm -rf /tmp/${DIR}
mkdir /tmp/${DIR}
git archive `git branch | grep '\*'| sed 's/^\* //g'` | tar -x -C /tmp/${DIR}
rm -rf /tmp/${DIR}/docs/
rm -rf /tmp/${DIR}/unit_test_data
rm -rf /tmp/${DIR}/.idea
rm -rf /tmp/${DIR}/Makefile
rm -rf /tmp/${DIR}/.git*
rm -rf /tmp/${DIR}/scripts
rm -rf /tmp/${DIR}/pylintrc
find /tmp/${DIR} -name test*.py -delete
find /tmp/${DIR} -name *_test.py -delete
rm -rf /tmp/${DIR}/*.bat
mkdir -p /tmp/${DIR}/docs/build
cp -r docs/build/html /tmp/${DIR}/docs/build/html
pushd .
cd /tmp/
# The \* tells zip to ignore recursively
rm ${OUT}
zip -r ${OUT} ${DIR} --exclude \*.pyc \
              ${DIR}/docs/source\* \
              ${DIR}/docs/*.jpeg\
              ${DIR}/docs/*.jpg\
              ${DIR}/docs/*.odf\
              ${DIR}/docs/*.png\
              ${DIR}/docs/build/doctrees\* \
              ${DIR}/docs/build/html\.buildinfo\* \
              ${DIR}/docs/cloud_sptheme\* \
              ${DIR}/docs/Flyer_InaSafe_FINAL.pdf \
              ${DIR}/.git\* \
              ${DIR}/*.bat \
              ${DIR}/.gitattributes \
              ${DIR}/.settings\* \
              ${DIR}/.pydev\* \
              ${DIR}/.coverage\* \
              ${DIR}/.project\* \
              ${DIR}/.achievements\* \
              ${DIR}/Makefile \
              ${DIR}/scripts\* \
              ${DIR}/impossible_state.* \
              ${DIR}/riab_demo_data\* \
              ${DIR}/\*.*~ \
              ${DIR}/\*test_*.py \
              ${DIR}/\*.*.orig \
              ${DIR}/\*.bat \
              ${DIR}/\*.xcf \
              ${DIR}/~ 
              
popd


echo "Your plugin archive has been generated as"
ls -lah ${OUT}
echo "${OUT}"
