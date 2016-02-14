#!/bin/sh
##
## Samza helper script to manage an application.
##

# INPUT
VERSION=$1
ACTION=$2

# App details
APP=<SAMZA APP>
APP_USER=<USER TO RUN AS>

# Where things should be found on the filesystem
# /opt/${APP}/${APP}-${VERSION}-dist.tar.gz -> your packaged samza app
# /opt/${APP}/${VERSION} -> extract of ${APP}-${VERSION}-dist.tar.gz
ROOT_PATH=/opt/${APP}
APP_PATH=/opt/${APP}/${VERSION}
APP_PKG=${APP}-${VERSION}-dist.tar.gz
APPLICATION_ID='UNKNOWN'

distribute()
{
    echo "Distributing application..."

    if [ ! -e "${ROOT_PATH}/${APP_PKG}" ]; then
        echo "Application package not present - expected at ${ROOT_PATH}/${APP_PKG}"
        exit 1
    fi

    # Extract package if required
    if [ ! -d "${APP_PATH}" ]; then
        mkdir -p ${APP_PATH}
        tar xzf ${ROOT_PATH}/${APP_PKG} -C ${APP_PATH}
        chown -R ${APP_USER}:${APP_USER} ${APP_PATH}
    fi

    # Create user directory on HDFS if it doesn't exist
    ret=$(su - hdfs -c "hdfs dfs -test -d /user/${APP_USER}")
    if [ $? -ne 0 ]; then
        echo "Creating hdfs:///user/${APP_USER}"
        su - hdfs -c "hdfs dfs -mkdir /user/${APP_USER}"
        su - hdfs -c "hdfs dfs -chown ${APP_USER}:${APP_USER} /user/${APP_USER}"
    fi

    ret=$(su - ${APP_USER} -c "hdfs dfs -test -d /user/${APP_USER}/${APP}")
    if [ $? -ne 0 ]; then
        echo "Creating /user/${APP_USER}/${APP}"
        su - ${APP_USER} -c "hdfs dfs -mkdir /user/${APP_USER}/${APP}"
    fi

    ret=$(su - ${APP_USER} -c "hdfs dfs -test -e /user/${APP_USER}/${APP}/${APP_PKG}")

    if [ $? -ne 0 ]; then
        echo "Uploading ${ROOT_PATH}/${APP_PKG} to hdfs:///user/${APP_USER}/${APP}"
        su - ${APP_USER} -c "hdfs dfs -put ${ROOT_PATH}/${APP_PKG} /user/${APP_USER}/${APP}"
    fi
}

hdfs_clean()
{
    echo "Cleaning hdfs:///user/${APP_USER}/${APP}/${APP_PKG}"
    su - ${APP_USER} -c "hdfs dfs -rm /user/${APP_USER}/${APP}/${APP_PKG}"
}

local_clean()
{
    echo "Cleaning ${APP_PATH}"
    rm -fr ${APP_PATH}
    echo "Cleaning ${ROOT_PATH}/${APP_PKG}"
    rm -f  ${ROOT_PATH}/${APP_PKG}
}

start() {
    echo "Starting application..."
    su - ${APP_USER} -c "${APP_PATH}/bin/run-job.sh \
        --config-factory=org.apache.samza.config.factories.PropertiesConfigFactory \
        --config-path=file://${APP_PATH}/config/${APP}.properties 2>&1 > ${APP_PATH}/run-job.log"
}

get_application_id()
{

    ret=$(grep 'Submitted application application_' ${APP_PATH}/run-job.log)
    if [ $? -ne 0 ]; then
        APPLICATION_ID="UNKNOWN"
    else
        APPLICATION_ID=$(echo "$ret" | sed -e 's/.* \(application_.*\)$/\1/')
    fi

}

stop()
{

    get_application_id
    if [ "$APPLICATION_ID" == "UNKNOWN" ]; then
        echo "Application ID can't be found"
        return 1
    else
        echo "Stopping $APPLICATION_ID"
        su - ${APP_USER} -c "yarn application -kill $APPLICATION_ID"
    fi
}

deploy()
{
    echo "Deploying application..."
    distribute
    start
}

undeploy()
{
    echo "Undeploying application..."
    stop
    hdfs_clean
    local_clean
}

help()
{
    echo "$0 VERSION ACTION"
}

if [ -z "$VERSION" ]; then
    echo 'VERSION not provided'
    help
    exit 1
fi

if [ -z "$ACTION" ]; then
    echo 'ACTION not provided'
    help
    exit 1
fi

case $ACTION in
    start)
        deploy
        exit $?
    ;;

    deploy)
        deploy
        exit $?
    ;;

    undeploy)
        undeploy
        exit $?
    ;;

    stop)
        stop
        exit $?
    ;;

    *)
        echo "Invalid ACTION $ACTION"
        help
        exit 1
    ;;
esac

