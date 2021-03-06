# sitemon
## _An Internet URL monitoring solution_

Sitemon is a python app to monitor http/https URLs and provide Prometheus metrics.

It can be deployed in a Kubernetes cluster, or ran in a container, or as a standalone script in a shell.

It uses the requests module to connect (using GET) to the URLs, which are configurable. It gets the HTTP status code and elapsed time from the response object, and provides these as the metrics.  It has a main loop wherein it probes the URL's and then sleeps for a set interval before probing them again.  It uses the prometheus_client module to run a simple http server to serve the metrics.


## Metrics provided
There are two metrics that are provided by the app for each URL.
1. sample_external_url_up
   - metrics type is gauge
   - boolean value of 1 or 0
   - if HTTP status code is 200, then this is set to 1 otherwise it is set to 0
2. sample_external_url_response_ms
   - metrics type is gauge
   - this is the elapsed time property from the requests response object
   - this is elapsed time in milliseconds

## Configuration
There are three settings that can be configured.  These are set via environment variables.  These can be set in the deployment definition, if the app is to be deployed on Kubernetes.

1. Port

   ```export SITEMON_METRICSPORT=8000```
   
   This is the TCP port number that the http server (provided by the prometheus_client) will listen on to serve the metrics info.  If not set, then the app will raise an exception and exit.

2. URLs
   
   ```export SITEMON_URLS="https://httpstat.us/200,https://httpstat.us/503"```
   
   This is the list of URL's to probe.  It must be comma-delimited.  If not set, then the app will raise an exception and exit.

3. Probe interval
   
   ```export SITEMON_INTERVAL=60```
   
   This is the interval (in seconds) between probes.  If not set, then a default of 60 will be used.


## Usage

### How to deploy sitemon on a Kubernetes cluster
If you have an existing Kubernetes cluster, you can deploy sitemon using the following [deployment YAML](sitemon-deployment.yaml).  This would use the pre-built image that is available in dockerhub.  If you want to build the image, then see the instructions in section "[How to build the container image](#how-to-build-the-container-image)".
Make sure to change the environment variables as appropriate for your setting.
```
apiVersion: apps/v1
kind: Deployment
metadata:
  labels:
    app: sitemon
  name: sitemon
spec:
  replicas: 1
  selector:
    matchLabels:
      app: sitemon
  template:
    metadata:
      labels:
        app: sitemon
    spec:
      containers:
      - image: alexisv914/sitemon:0.1
        imagePullPolicy: Always
        name: sitemon
        env:
        - name: "SITEMON_METRICSPORT"
          value: "8000"
        - name: "SITEMON_URLS"
          value: "https://httpstat.us/503,https://httpstat.us/200"
        - name: "SITEMON_INTERVAL"
          value: "60"
```

You can save the above definition in a file (e.g., sitemon-deployment.yaml) and deploy to your cluster (e.g., sitemon namespace) by running:
```
kubectl create ns sitemon
kubectl -n sitemon apply -f sitemon-deployment.yaml
```

You can then examine the pod status and logs to verify that the app is working as expected.
![kubectl output](sitemon-examine.png)

You would need to expose the application through a service (e.g., NodePort) or some form of ingress, so that your Prometheus server could scrape the metrics info from the app.  Once exposed you should be able to access the metrics info from http://$nodeIP:$port/metrics.  This metrics URL must be accessible by the Prometheus server.

#### Screenshot of metrics info:
![metrics info](metrics.png)
   
   
### How to run sitemon in a container
You would need docker installed in the host where you run this.

You can use the pre-built image that is available in dockerhub.  If you want to build the image, then see the instructions in section "[How to build the container image](#how-to-build-the-container-image)"

You can run the following to start the container.  
```
docker run -d -p 8000:8000 -e SITEMON_METRICSPORT=8000 -e SITEMON_URLS="https://httpstat.us/503,https://httpstat.us/200" -e SITEMON_INTERVAL=60 --name="sitemon" alexisv914/sitemon:0.1
```
Once running you should be able to access the metrics info from http://localhost:8000/metrics.

   
### How to run sitemon in a shell
You would need python3 installed where you run this.
```
export SITEMON_METRICSPORT=8000
export SITEMON_URLS="https://httpstat.us/503,https://httpstat.us/200"
export SITEMON_INTERVAL=60
python3 app.py
```
Once running you should be able to access the metrics info from http://localhost:8000/metrics.

   
### How to build the container image
You can use the following files from this repo to build the container image:

- [Dockerfile](Dockerfile)
- [requirements.txt](requirements.txt)
- [app.py](app.py)

To build the image, you can run the following command in the same directory where the above files are located.
```
docker build --tag=alexisv914/sitemon:0.1 .
```
Once the build is completed, you should see it in the list of your docker images.
```
docker images
REPOSITORY                       TAG         IMAGE ID       CREATED        SIZE
alexisv914/sitemon               0.1         e9971092ad11   3 hours ago    131MB
```

   
## Integrating with Prometheus and Grafana
Once you have the app running and the metrics URL accessible, you should now be able to configure your Prometheus deployment to scrape the metrics info from the metrics URL.

The following is an example configuration that you can add to your Prometheus config to use the sitemon metrics.  In this example, the metrics URL is http://localhost:80/metrics.
```
scrape_configs:
    # The job name is added as a label `job=<job_name>` to any timeseries scraped from this config.
    - job_name: 'sample_external_url'
      # metrics_path defaults to '/metrics'
      # scheme defaults to 'http'.
      static_configs:
        - targets: ['localhost:80']
```
You can then restart Prometheus after adding the config similar to the above.  Afterwards, you can create the dashboard and panels in Grafana using the sitemon metrics from Prometheus. 

#### Screenshot of Prometheus UI showing the sample_external_url_response_ms metric:
![prometheus sample_external_url_response_ms](prometheus-sample_external_url_response_ms.png)


#### Screenshot of Prometheus UI showing the sample_external_url_up metric:
![prometheus sample_external_url_up](prometheus-sample_external_url_up.png)


#### Screenshot of Grafana Dashboard showing the panels with the metrics:
![grafana dashboard](grafana-dashboard-sitemon.png)   
   

## Unit Tests
You can run [test_app.py](test_app.py) for the unit tests on getstat() and getsettings() functions.
```
python3 test_app.py
```
The tests include the following assertions among others:
- exception is raised if SITEMON_METRICSPORT or SITEMON_URLS is missing or invalid
- the tuple item for "up" returned by getstat() is set to 0 for connection errors or invalid URLs


