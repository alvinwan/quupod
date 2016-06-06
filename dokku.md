Install dokku:
http://dokku.viewdocs.io/dokku/


# Deployment Setup
Add public key to dokku then,

git remote add dokku dokku@app.cs61a.org:quupod

# Deploy (from master branch)
git push dokku master

# Setup

## Plugin Installation:
(run under ubutu user when sshed in)
sudo dokku plugin:install https://github.com/dokku/dokku-mysql.git mysql

## App Creation
dokku apps:create quupod
dokku mysql:create quupod
dokku mysql:link quupod quupod
dokku config:set quupod GOOGLECLIENTID=foo
dokku domains:add quupod oh.cs61a.org # (also update DNS record of oh.cs61a.org to point to IP)
dokku config:set quupod DOMAIN=http://quupod.app.cs61a.org
dokku storage:mount quupod /var/lib/dokku/data/storage:/storage
scp client_secrets.json ubuntu@app.cs61a.org:/var/lib/dokku/data/storage/

# SSL
dokku letsencrypt quupod #(assuming the letsencrypt plugin is installed)
dokku config:set quupod DOMAIN=https://oh.cs61a.org

# Commands:
If needed:
`dokku run quupod <your command>`

dokku run quupod 'bash'
$ echo  'contents of client_secrets' > client_secrets.json

## Suggestions
`alias dokku=ssh -t dokku@app.cs61a.org`
