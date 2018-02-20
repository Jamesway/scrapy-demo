# Docker-Laravel
Dockerized Laravel Web Framework Container

Use this repo to create a Laravel container ready for development.

Requirements: Docker, and Docker-sync (Mac)

## Create a Laravel or Laravel Lumen Project

### Composer
Inside of an empty directory:

```
docker run --rm -v $(pwd):/app composer create-project --prefer-dist laravel/laravel .
OR
docker run --rm -v $(pwd):/app composer create-project --prefer-dist laravel/lumen .

docker run --rm -v $(pwd):/app composer php artisan app:name CustomNamespace

docker run --rm -v $(pwd):/app composer dump-autoload
```


Copy or pull the contents of this repo into your project directory.

*Note: you can overwrite laravel's default README with this one*


### Docker-Sync
Docker machine uses virtualbox as it's vm. If your Mac is newer than 2011, you can use Docker for Mac.
Virtualbox doesn't pass on INotify from the guest to the host so file changes are very slow to register.
Docker-sync is a container that makes file changes via Unison or Rsync.

```gem install docker-sync```

Adjust docker-sync.yml for your needs

```docker-sync start```

*Note: when you need to stop docker-sync, it's a good idea to "clean"*
```
docker-sync stop
docker-sync clean
```

- Bring up the stack (with docker-sync running)

```docker-compose up -d```

*Note: In case you encounter the Error:*

  ERROR: Service 'php-cli' failed to build: Unknown flag: from

  *This error is due to Docker Server version not supporting multi-stage build. Use the following command to upgrade Docker Server version:*

  ```docker-machine upgrade default```

## Docker Maintenance

From time to time its a good idea to purge unused containers, volumes and images.

### Images
To list docker images and remove
```
docker images

docker rmi [image id] #the first 3 characters are usually unique enough
```

### Containers
To list RUNNING containers

```docker ps```

*Note: You can't/shouldn't remove a running container without stopping it, but listing the running containers gives you an idea if any container isn't running when it should be. For instnance, if mariadb isn't running, you can explicitly run that container - ```docker-compose run mariadb``` - and the start messages will display suggesting it might be a good idea to purge volumes.*

To list stopped containers and remove
```
docker ps -a

docker rm [container id] #the first 3 characters are usually unique enough

docker rm -v [container id] #removes volumes with container
```


### Volumes
To list volumes

```docker volume ls```

To delete volumes

```docker volume rm [volume id]```

To list and remove dangling volumes that have no containers
```
docker volume ls -f dangling=true

docker volume rm $(docker volume ls -q -f dangling=true)
```
*Note: to prevent dangling volumes use [-v] when removing containers - docker rm -v [container id]*



## **Testing**

### phpspec

#### adjust the namespaces on phpspec.yml to your project's namespace

#### create a class
```docker run -itv --rm -v $(pwd):/app phpspec/phpspec desc "Class"```

#### test the class
```docker run -itv --rm -v $(pwd):/app phpspec/phpspec run "Class"```

#### run the entire test suite
```docker run -itv --rm -v $(pwd):/app phpspec/phpspec run```


## **Xdebug and PhpStorm**

### Network Alias
Docker on Mac as an issue with outbound communication so as a workaround, create an alias to the "xdebug.remote_host" in the php-fpm dockerfile (172.254.254.254). It doesn't matter what IP is, but they have to match. If you restart your Mac you may need to re-alias.

```sudo ifconfig en0 alias 172.254.254.254 255.255.255.0```

*Note: if running Docker for Mac, you can skip the alias by setting "xdebug.remote_host" to docker.for.mac.localhost (untested)*

### PhpStorm (as of 2017.2)

#### Debug
![Alt text](./README/phpstorm-debug.png)

Open Preferences -> Languages & Frameworks -> PHP -> Debug
- Under "Xdebug" make sure the "Debug port" is the same as "xdebug.remote_port" in the php-fpm dockerfile (9000)
- make sure "Can accept external connections" is checked

#### DBGp Proxy
![Alt text](./README/phpstorm-dbgp-proxy.png)

Open Preferences -> Languages & Frameworks -> PHP -> Debug -> DBGp Proxy
- Set IDE Key to the same key as "xdebug.idekey" in the php-fpm dockerfile (PHPSTORM)
- Set Host to the same IP as "xdebug.remote_host" in the php-fpm dockerfile (172.254.254.254)
- Set Port to the same port as "xdebug.remote_port" in the php-fpm dockerfile (9000)

#### Servers
![Alt text](./README/phpstorm-servers.png)

Open Preferences -> Languages & Frameworks -> Servers
- Add a new server for this project (+), the name can be anything
- Host must match the nginx server_name directive in vhost.conf (locahost)
- Set port to 80
- Check "use path mappings" and set the local public directory to the servers public directory (for nginx /var/www/public)

### Chrome Plugin Xdebug helper

Install the plugin: https://chrome.google.com/webstore/detail/xdebug-helper/eadndfjplgieldjbigjakmdgkmoaaaoc?hl=en

Right click on the bug icon and select "Options"

![Alt text](./README/xdebug-helper-settings.png)

Under "Ide key" select "PhpStorm" and enter the same key as "xdebug.idekey" in the php-fpm dockerfile (PHPSTORM)

### Using Xdebug with PhpStorm

```docker-compose up -d```

![Alt text](./README/phpstorm-listen.png)

In PhpStorm, Listen for debug connections and set a break point


![Alt text](./README/xdebug-helper-enable.png)

Reload in chrome with xdebug helper enabled and PhpStorm should take focus and allow you to step through
