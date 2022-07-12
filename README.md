# GuideVar
Predict on-target efficiency and off-target effects of Cas9 variants

## Installation with Docker

With Docker, no installation is required - the only dependence is Docker itself. Users will not need to deal with installation and configuration issues.

Docker can be downloaded freely here: [https://store.docker.com/search?offering=community&type=edition](https://store.docker.com/search?offering=community&type=edition)

Following the installation of Docker, simply execute the following command in the terminal for a local version of PrimeDesign:
* ```docker pull hwkobe/guidevar```


## Run GuideVar with command line tool

Run the GuideVar-on command line interface (CLI) with the command in the terminal:

```
docker run -v ${PWD}/:/DATA -w /DATA hwkobe/guidevar guidevar-on [options]
```


Run the GuideVar-off command line interface (CLI) with the command in the terminal:

```
docker run -v ${PWD}/:/DATA -w /DATA hwkobe/guidevar guidevar-off [options]
```

