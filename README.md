Websocket Server Example
========================
Nathan Schwermann
-----------------


Requires python, tornado, and nginx

`pip install tornado`

`python sockets.py`

Visit the webpage demo at http://localhost/list using the NGINX site configuration below
(it is possible to use without nginx but sockets.py will need to be tweaked to load static files)

    upstream tornado {
      server 127.0.0.1:8888;
    }

    server {
      listen 80 default; ## listen for ipv4; this line is default and implied
      #listen   [::]:80 default ipv6only=on; ## listen for ipv6

      root /var/www;
      index index.html index.htm index.php;

      # Make site accessible from http://localhost/
      server_name localhost;

      location / {
        # First attempt to serve request as file, then
        # as directory, then fall back to index.html
        try_files $uri $uri/ /index.html;
        # Uncomment to enable naxsi on this location
        # include /etc/nginx/naxsi.rules
      }

      location /list/static/{

      }

      location /list {
        root /var/www/list/;
        if ($query_string) {
          expires max;
        }
        proxy_pass http://tornado;
        proxy_http_version 1.1;
        proxy_pass_header Server;
        proxy_redirect off;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
      }

      location /doc/ {
        alias /usr/share/doc/;
        autoindex on;
        allow 127.0.0.1;
        deny all;
      }

    }

The following supervisor configuration can be used to keep the tornado instance running

    [program:tornado]
    command=python /var/www/list/sockets.py
    stdout_logfile=/var/www/list/log.txt
    redirect_stderr=true
