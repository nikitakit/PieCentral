#!/bin/bash

##############################################################################################
# Pulls the newest versions of PieCentral from github and packages hibike and runtime nicely #
# in a tarball along with the install_update.sh script.                                      #
##############################################################################################

FRANKFURTER_DIR=$(git rev-parse --show-toplevel)/DevOps/frankfurter
BUILD_DIR=$FRANKFURTER_DIR/build
TMP_DIR=$BUILD_DIR/tmp
PROTO_DIR=$(git rev-parse --show-toplevel)/ansible-protos
RUNTIME_PROTO=$(git rev-parse --show-toplevel)/runtime/testy

if [ -d "$BUILD_DIR" ]; then
    echo "Cleaning old builds ... "
    rm -rf $BUILD_DIR/*
else
    echo "Making build directory ... "
    mkdir -p $BUILD_DIR
fi
mkdir -p $TMP_DIR
echo "Done."


git pull origin master
<<<<<<< HEAD

protoc PROTO_DIR/runtime.proto --python_out=RUNTIME_PROTO


=======
>>>>>>> d3830b575389ba7d7b040c492c105e04b216b61a
# Copy hibike and runtime
cp -R $(git rev-parse --show-toplevel)/hibike $TMP_DIR/hibike
cp -R $(git rev-parse --show-toplevel)/runtime $TMP_DIR/runtime
cp $FRANKFURTER_DIR/scripts/update/install_update.sh $TMP_DIR

CURRENT_TIME=$(date +%s%N)
UPDATE_FILENAME=frankfurter-update-"$CURRENT_TIME".tar.gz

cd $TMP_DIR
tar -zcf $BUILD_DIR/$UPDATE_FILENAME *
printf "\x1b[1;32m"
echo "==> Tarball available at: "
echo $BUILD_DIR/$UPDATE_FILENAME
printf "\x1b[0m"

cd ..
rm -rf $TMP_DIR
echo "Cleaned up."
