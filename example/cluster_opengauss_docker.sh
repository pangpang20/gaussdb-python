#!/bin/bash
# create master and slave
# Copyright (c) Huawei Technologies Co., Ltd. 2020-2028. All rights reserved.
#
#openGauss is licensed under Mulan PSL v2.
#You can use this software according to the terms and conditions of the Mulan PSL v2.
#You may obtain a copy of Mulan PSL v2 at:
#
#          http://license.coscl.org.cn/MulanPSL2
#
# THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND,
# EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT,
# MERCHANTABILITY OR FIT FOR A PARTICULAR PURPOSE.
# See the Mulan PSL v2 for more details.
#-------------------------------------------------------------------------
#
# create_master_slave.sh
#    create master and slave
#
# IDENTIFICATION
#    GaussDBKernel/server/docker/dockerfiles/create_master_slave.sh
#
#-------------------------------------------------------------------------

#set OG_SUBNET,GS_PASSWORD,MASTER_IP,SLAVE_1_IP,MASTER_HOST_PORT,MASTER_LOCAL_PORT,SLAVE_1_HOST_PORT,SLAVE_1_LOCAL_PORT,MASTER_NODENAME,SLAVE_NODENAME

# Define default values
NETWORK_NAME="opengaussnetwork"
GS_USERNAME=root
OG_SUBNET="172.11.0.0/24"
MASTER_IP="172.11.0.101"
MASTER_HOST_PORT="5432"
MASTER_NODENAME="dn_6001"

VERSION="7.0.0-RC1"

# Define default values for slaves
SLAVE_IP=("172.11.0.102" "172.11.0.103" "172.11.0.104" "172.11.0.105" "172.11.0.106" "172.11.0.107" "172.11.0.108" "172.11.0.109")
SLAVE_HOST_PORT=("6432" "7432" "8432" "9432" "10432" "11432" "12432" "13432")
SLAVE_NODENAME=("dn_6002" "dn_6003" "dn_6004" "dn_6005" "dn_6006" "dn_6007" "dn_6008" "dn_6009")
SLAVE_COUNT=2
BASE_DIR="/opt/opengauss_data"
MASTER_OUT_DIR="${BASE_DIR}/dn_6001"
SLAVE_OUT_DIR=("${BASE_DIR}/dn_6002" "${BASE_DIR}/dn_6003")

log(){ echo -e "[$(date '+%F %T')] $*"; }

wait_for_db(){
    local cname="$1" port="$2"
    local max=60; local i=0
    until docker exec "$cname" su - omm -c "gsql -d postgres -U omm -p \"$port\" -c '\q'" >/dev/null 2>&1; do
        ((i++)); if (( i>=max )); then echo "ERROR: $cname not ready"; exit 1; fi
        sleep 5; log "$LINENO:Waiting $cname ..."
    done
}

if [ -z "${GS_PASSWORD:-}" ]; then
    echo "Please enter a password with at least 8-16 digits containing numbers, letters, and special characters: "
    read -s GS_PASSWORD
fi

if [[ "$GS_PASSWORD" =~  ^(.{8,}).*$ ]] &&  [[ "$GS_PASSWORD" =~ ^(.*[a-z]+).*$ ]] && [[ "$GS_PASSWORD" =~ ^(.*[A-Z]).*$ ]] &&  [[ "$GS_PASSWORD" =~ ^(.*[0-9]).*$ ]] && [[ "$GS_PASSWORD" =~ ^(.*[#?!@$%^&*-]).*$ ]]; then
    log "$LINENO:The supplied GS_PASSWORD is meet requirements."
else 
    log "$LINENO:Please Check if the password contains uppercase, lowercase, numbers, special characters, and password length(8). At least one uppercase, lowercase, numeric, special character."
    exit 1
fi

ARGS=$(getopt -o h --long OG_SUBNET:,GS_PASSWORD:,MASTER_IP:,MASTER_HOST_PORT:,MASTER_LOCAL_PORT:,MASTER_NODENAME:,VERSION:,SLAVE_COUNT:,NETWORK_NAME: -- "$@")
if [ $? != 0 ]; then
    echo "Argument parsing error"
    exit 1
fi
eval set -- "$ARGS"

# Use getopts to process command line arguments
while true; do
    case "$1" in
        -h)
            echo "Usage: $0 [--OG_SUBNET value] [--GS_PASSWORD value] [--MASTER_IP value] [--MASTER_HOST_PORT value] [--MASTER_NODENAME value] [--VERSION value] [--SLAVE_COUNT value] [--NETWORK_NAME value]"
            shift
            ;;
        --OG_SUBNET)
            OG_SUBNET="$2"
            shift 2
            ;;
        --GS_PASSWORD)
            GS_PASSWORD="$2"
            shift 2
            ;;
        --MASTER_IP)
            MASTER_IP="$2"
            shift 2
            ;;
        --MASTER_HOST_PORT)
            MASTER_HOST_PORT="$2"
            shift 2
            ;;
        --MASTER_LOCAL_PORT)
            MASTER_LOCAL_PORT="$2"
            shift 2
            ;;
        --MASTER_NODENAME)
            MASTER_NODENAME="$2"
            shift 2
            ;;
        --VERSION)
            VERSION="$2"
            shift 2
            ;;
        --SLAVE_COUNT)
            SLAVE_COUNT="$2"
            shift 2
            ;;
        --NETWORK_NAME)
            NETWORK_NAME="$2"
            shift 2
            ;;
        --)
            shift
            break
            ;;
        *)
            echo "Invalid option: -$OPTARG" >&2
            exit 1
            ;;
    esac
done

# Output the set values
log "$LINENO:OG_SUBNET set $OG_SUBNET"
log "$LINENO:MASTER_IP set $MASTER_IP"
log "$LINENO:MASTER_HOST_PORT set $MASTER_HOST_PORT"
log "$LINENO:MASTER_NODENAME set $MASTER_NODENAME"
log "$LINENO:openGauss VERSION set $VERSION"
log "$LINENO:SLAVE_COUNT set $SLAVE_COUNT"
log "$LINENO:SLAVE_NODENAME set $SLAVE_NODENAME"
log "$LINENO:SLAVE_IP set $SLAVE_IP"
log "$LINENO:SLAVE_HOST_PORT set $SLAVE_HOST_PORT"
log "$LINENO:NETWORK_NAME set $NETWORK_NAME"

# Loop through and process each slave's information
for (( i=0; i<SLAVE_COUNT; i++ )); do
    log "$LINENO:SLAVE_${i}_IP set${SLAVE_IP[$i]}"
    log "$LINENO:SLAVE_${i}_HOST_PORT set${SLAVE_HOST_PORT[$i]}"
    log "$LINENO:SLAVE_${i}_NODENAME set${SLAVE_NODENAME[$i]}"
done


log "$LINENO:Starting..."
log "$LINENO:Reset data dirs..."
rm -rf "$BASE_DIR"
mkdir -p "$MASTER_OUT_DIR" "${SLAVE_OUT_DIR[@]}"

log "$LINENO:Cleaning up existing containers and network..."
for name in "$MASTER_NODENAME" "${SLAVE_NODENAME[@]}"; do
    if [ "$(docker ps -a -q -f name=^/${name}$)" ]; then
        log "$LINENO:Removing existing container $name"
        docker rm -f $name >/dev/null || true
    fi
done

if [ "$(docker network ls -q -f name=^${NETWORK_NAME}$)" ]; then
    log "$LINENO:Removing existing network $NETWORK_NAME"
    docker network rm $NETWORK_NAME >/dev/null || true
fi

log "$LINENO:Creating OpenGauss Database Network..."
docker network create --subnet=$OG_SUBNET $NETWORK_NAME \
|| { echo "ERROR: Network was NOT successfully created."; exit 1; }
log "$LINENO:OpenGauss Database Network Created."

log "$LINENO:Creating OpenGauss Database Master Docker Container..."
REPL_CONN_INFO_MASTER=""
local_info="localhost=$MASTER_IP localport=$((MASTER_HOST_PORT+1)) localservice=$((MASTER_HOST_PORT+4)) localheartbeatport=$((MASTER_HOST_PORT+5))"
for (( i=0; i<SLAVE_COUNT; i++ )); do
    remote_port=${SLAVE_HOST_PORT[$i]}
    remote_info="remotehost=${SLAVE_IP[$i]} remoteport=$((remote_port+1)) remoteservice=$((remote_port+4)) remoteheartbeatport=$((remote_port+5))"
    REPL_CONN_INFO_MASTER+="replconninfo$((i+1)) = '$local_info $remote_info'\n"
done
docker run --network $NETWORK_NAME --ip $MASTER_IP --privileged=true \
--name $MASTER_NODENAME -h $MASTER_NODENAME -p $MASTER_HOST_PORT:$MASTER_HOST_PORT -d \
-v $MASTER_OUT_DIR:/var/lib/opengauss \
-e GS_USERNAME=$GS_USERNAME \
-e GS_PORT=$MASTER_HOST_PORT \
-e OG_SUBNET=$OG_SUBNET \
-e GS_USER_PASSWORD="$GS_PASSWORD" \
-e GS_PASSWORD="$GS_PASSWORD" \
-e NODE_NAME="$MASTER_NODENAME" \
-e REPL_CONN_INFO="$REPL_CONN_INFO_MASTER" \
opengauss:$VERSION -M primary > /dev/null 

log "$LINENO:OpenGauss Database Master Docker Container created."
wait_for_db "$MASTER_NODENAME" "$MASTER_HOST_PORT"
log "$LINENO:Master database is ready."


for (( i=0; i<SLAVE_COUNT; i++ )); do
    REPL_CONN_INFO_SLAVE=""
    local_port=${SLAVE_HOST_PORT[$i]}
    log "$LINENO:Creating slave ${SLAVE_NODENAME[$i]} on ${SLAVE_IP[$i]}:$local_port ..."
    local_info="localhost=${SLAVE_IP[$i]} localport=$((local_port+1)) localservice=$((local_port+4)) localheartbeatport=$((local_port+5))"
    remote_master_info="remotehost=$MASTER_IP remoteport=$((MASTER_HOST_PORT+1)) remoteservice=$((MASTER_HOST_PORT+4)) remoteheartbeatport=$((MASTER_HOST_PORT+5))"
    k=1
    REPL_CONN_INFO_SLAVE="replconninfo${k} = '$local_info $remote_master_info'\n"
    for (( j=0; j<SLAVE_COUNT; j++ )); do
        if [[ $i -eq $j ]]; then
            continue
        fi
        k=$((k+1))
        remote_port=${SLAVE_HOST_PORT[$j]}
        remote_info="remotehost=${SLAVE_IP[$j]} remoteport=$((remote_port+1)) remoteservice=$((remote_port+4)) remoteheartbeatport=$((remote_port+5))"
        REPL_CONN_INFO_SLAVE+="replconninfo${k} = '$local_info $remote_info'\n"
    done

    docker run --network $NETWORK_NAME --ip ${SLAVE_IP[$i]} --privileged=true \
    --name ${SLAVE_NODENAME[$i]} -h ${SLAVE_NODENAME[$i]} -p $local_port:$local_port -d \
    -v ${SLAVE_OUT_DIR[$i]}:/var/lib/opengauss \
    -e GS_PORT=$local_port \
    -e OG_SUBNET=$OG_SUBNET \
    -e GS_PASSWORD="$GS_PASSWORD" \
    -e NODE_NAME="${SLAVE_NODENAME[$i]}" \
    -e REPL_CONN_INFO="$REPL_CONN_INFO_SLAVE" \
    opengauss:$VERSION -M standby > /dev/null

    wait_for_db "${SLAVE_NODENAME[$i]}" "$local_port"
    log "$LINENO:${SLAVE_NODENAME[$i]} database is ready."
done

log "$LINENO:All nodes are up."
