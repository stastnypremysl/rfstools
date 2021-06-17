#!/bin/bash
git pull

new_version=$(cat ./version.txt)
if git tag | grep -xF "$new_version" >/dev/null; then
  echo "This version have been already deployed."
  exit 1
fi

git add -A
git commit -m "new version $new_version"
git tag $(cat ./version.txt)

git push
git push --tags
