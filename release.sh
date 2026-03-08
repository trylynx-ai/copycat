#!/bin/bash

set -e

git checkout release
git merge main --ff-only
git push origin release
