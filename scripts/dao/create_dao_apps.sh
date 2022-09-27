#!/bin/bash

source env

## create app
dao install $DAO_ADDRESS agent --env $DEPLOY_ENV
dao install $DAO_ADDRESS agent --env $DEPLOY_ENV

# aragon apm info ownership-voting.open.aragonpm.eth --env aragon:rinkeby --ipfs-rpc https://api.pinata.cloud --ipfs-gateway https://gateway.pinata.cloud/ipfs
dao install $DAO_ADDRESS ownership-voting.open.aragonpm.eth --app-init-args $VOTING_ESCROW 510000000000000000 300000000000000000 86400 2500 10 2500 50000 10 1000 --env $DEPLOY_ENV --ipfs-rpc https://ipfs.infura-ipfs.io:5001/ --ipfs-gateway https://ipfs.infura-ipfs.io/ipfs

dao install $DAO_ADDRESS create-guild-voting.open.aragonpm.eth --app-init-args $VOTING_ESCROW 510000000000000000 300000000000000000 86400 2500 1000000 10 2500 50000 1000000 1000000000 10 1000 --env $DEPLOY_ENV --ipfs-rpc https://ipfs.infura-ipfs.io:5001/ --ipfs-gateway https://ipfs.infura-ipfs.io/ipfs

dao apps $DAO_ADDRESS --all --env $DEPLOY_ENV
dao acl view $DAO_ADDRESS --env $DEPLOY_ENV
