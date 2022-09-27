#!/bin/bash

source env
echo $DEPLOY_ENV
dao new --env $DEPLOY_ENV
