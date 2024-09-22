# Servier - Data Engineering Test by Hussein Ballouk

This repository hosts the codebase for Servier's Data Engineering technical test. 

The test focuses on analyzing journals referenced by PubMed articles and clinical trials, utilizing input data in the form of .csv and .json files. T

he primary goal is to generate a link graph that illustrates the connections between journals and the drugs mentioned in the titles of the articles.


# Table of contents :

- [Servier - Data Engineering Test by Hussein Ballouk](#servier---data-engineering-test-by-hussein-ballouk)
- [Table of contents :](#table-of-contents-)
- [Section 1 - Python and Data Engineering](#section-1---python-and-data-engineering)
  - [I. Before we start - Hypothesis about the project data](#i-before-we-start---hypothesis-about-the-project-data)
  - [II. Requirements](#ii-requirements)
  - [III. Installation and packaging](#iii-installation-and-packaging)
  - [IV. Commands - Main code (Part 3) and Ad-hoc code (Part 4)](#iv-commands---main-code-part-3-and-ad-hoc-code-part-4)
  - [V. Adapt pipeline for production](#v-adapt-pipeline-for-production)
    - [A. Deployment](#a-deployment)
    - [B. Orchestration](#b-orchestration)
  - [VI. How to adapt the code for Big Data (Part 6)](#vi-how-to-adapt-the-code-for-big-data-part-6)
- [Section 2 - SQL](#section-2---sql)

# Section 1 - Python and Data Engineering
## I. Before we start - Hypothesis about the project data

The project was developed with the following hypothesis in mind :
- If an article does not mention a drug in its title, then we skip the article in the link graph.
- An article can mention one or multiple drugs in the same title. In this case, 2 instances of the same article are shown in the link graph (one per drug).
- We might have multiple input files to load data from, in `.csv` and `.json` format. This is the case for `pubmed.csv` and `pubmed.json` that should be loaded together.
- We can have broken `.json` input (trailing comma) and we need to take that into account.
- For the ad-hoc question, we can have multiple top journals if we have a tie in the number of unique drug mentions. In this case, we will return a list of all the tied journals.

## II. Requirements

Before we start, you should make sure that you have the following requirements in order to run the code on your computer :
- `Python >= 3.10.9` - Please install the appropriate version from the [official website](https://www.python.org/downloads/).
- `git` tool in order to clone the repository. If you prefer, you can simply download the repository under `Code > Download as Zip` but it is not recommended (easier to update the code with `git pull`).
- For packaging, you will need either `poetry` (downloaded using `pip install poetry`) or `docker` (downloaded from the [official website](https://www.docker.com/products/docker-desktop/)).


## III. Installation and packaging

If you have opted for `poetry` as your packaging tool, then you will need to run the following commands from the root level of the repository :
```cmd
poetry install
poetry shell
```

If you would rather run the container using `docker`, then i would recommend you to run the following commands from the root level of the repository :
```cmd
docker build -t test-servier-app:latest -f Dockerfile .
docker run -i -t test-servier-app:latest
```


## IV. Commands - Main code (Part 3) and Ad-hoc code (Part 4)

It is important to note that the commands in this section are run either in your `poetry shell` or `docker container bash`. Otherwise, you will have missing librairies.

Before running the main python application, you will need to run these two commands in order to setup your environment :
```cmd
cd app
export $(cat .env | xargs)
```

Now you can finally start running the python commaands. You can get familiar with all possible commands and **default values** by running the argparse helper function using `python app/main.py`.


Here is a list of commands to run for each use case  :
- [Main] - If you want to generate the link graph, using the `.env` variables : run `python main.py generate_graph_link`
- [Main] - If you prefer overwriting the input and output paths, you can do so with the following command and flags :
```
python main.py generate_graph_link --clinical_trials_paths '<PATH1.csv>' --pubmed_paths '<PATH1.csv>;<PATH2.csv>' --drugs_paths '<PATH1.csv>' --output_path '<OUTUPT.json>'
```
- [Ad-hoc] - To get the name(s) of the journal(s) mentioning the most unique drugs : run `python main.py get_top_journal`
- [Ad-hoc] - To get the name(s) of the drug(s) mentioned by non-clinical trials referenced journals, based on a specific drug mention : run `python main.py get_drug_mentions --adhoc_drug_name '<DRUG_NAME>'`


## V. Adapt pipeline for production
### A. Deployment

In order to setup a production-grade pipeline, some improvments can be made in the deployment section :
- Setup variables by environment to allow for easier testing and seperation of environments. So have `.env_dev` / `.env_ppd` / `.env_prd`.
- Setup a CI/CD using `Gitlab CI`, `Jenkins` or `Cloud Build` or any other tool in order to have a smooth "Development to Production" deployment.
- The CI/CD strategy can be any of the following :
  - A 3-branch (`develop`, `preprod`, `prod`) deployment strategy with triggers on `Merge Requests` .
  - A single `main` branch deployment strategy where :
    - A `Merge Request` triggers a deployment to the **dev** environment
    - A merge on the `main` branch triggers a deployment to the **ppd** environment
    - A tag on the `main` branch triggers a deployment to the **prd** environment.
- The tags should follow the Semantic Versioning model and rules.
- Run security, regression and end-to-end tests with reports using the CI/CD

### B. Orchestration

The codebase was written with `Composer` / `Airflow` in mind. We can run this code using 2 different methods :
- First, we can simply import the application and use `PythonOperator` to run our code. Snippet :
    ```python
    generate_graph_task = PythonOperator(
        task_id='generate_graph',
        provide_context=True,
        python_callable=main,
        op_kwargs={'param1': 'value1', 'param2': 'value2'}
        dag=dag,
    )
    ```
- Secondly, use a simple `BashOperator` to run the code with the commands seen above. Snippet : 
    ```python
    generate_graph_task= BashOperator(
        task_id="generate_graph",
        bash_command=f"export $(cat .env | xargs) && python main.py generate_graph_link"
    )
    ```
- Finally, a better option (for Big Data) would be to use `KubernetesPodOperator` instead.
  - The docker image will be built and pushed to **Artifact Registry** using the CI/CD.
  - Then in the `KubernetesPodOperator`, we can use the docker image and run the code using the commands seen above. Snippet :
    ```python
    generate_graph_task = KubernetesPodOperator(
        task_id="generate_graph",
        name="generate_graph",
        security_context=security_context,
        env_vars=env_variables,
        namespace=kub_pod_namespace,
        service_account_name=kub_pod_service_account,
        kubernetes_conn_id=kub_pod_connection_id,
        config_file=kub_pod_config_file,
        startup_timeout_seconds=600,
        is_delete_operator_pod=True,
        hostnetwork=False,
        image=my_docker_image_name,
        container_resources=pod_resources,
        retries=1,
        cmds=["/bin/bash", "-c"],
        arguments=["export $(cat .env | xargs) && python main.py generate_graph_link"],
    )
    ```

## VI. How to adapt the code for Big Data (Part 6)

In order to adapt the code for Big Data (Milions of rows, TB of data), we have two options for the **ETL** pipeline :
- Use `pySpark` instead of `pandas` so we can have distributed computation.
  - The adaptation of code should be straightforward since `pandas` and `pySpark` share similarities in syntax.
  - The code should be run on a **virtual machine** that has enough resources (GPU, CPU, memory).

- Otherwise, you can load the data on **BigQuery** and perform the ETL transformations using SQL :
  - The input files should be hosted on **Google Cloud Storage** so we can ingest them easily via bigquery.
  - The SQL transformations can be performed and "orchestrated" via a version controled `dbt` project
  - The output file should be written to **Google Cloud Storage** and lifecycle policies should be setup to avoid accidental loss of data.


Either way, you should also explore the new data and adapt the **unittests** as well as the **cleaning rules** used in the project so we can cover a wider scope.


# Section 2 - SQL

- Before we start, here is a list of hypothesis that I infered before solving the problems :
    - The tables are inside a dataset called `test_servier`
    - We will be using BigQuery's SQL notation
    - Since we are using BigQuery, then we assuume that the date will automatically be fixed and converted to %Y-%m-%d instead of %d/%m/%Y, so no need to use `FORMAT_DATE()` or `PARSE_DATE()` functions

- Part 1 : Daily sales between January 1st 2019 and December 31st 2019 => Check [query_1_sales_by_day.sql](sql/query_1_sales_by_day.sql)
```sql
SELECT
    date AS date,
    SUM(prod_price * prod_qty) AS ventes
FROM
    `test_sevrier.TRANSACTIONS`
WHERE
    date BETWEEN "2019-01-01" AND "2019-12-31"
GROUP BY
    date
ORDER BY
    date ASC
```


- Part 2 : Decoration and Furniture sales by client, between January 1st 2019 and December 31st 2019 => Check [query_2_sales_by_product_type.sql](sql/query_2_sales_by_product_type.sql)
```sql
SELECT
    t.client_id AS client_id,
    SUM(
        CASE
            WHEN pn.product_type = 'MEUBLE' THEN t.prod_price * t.prod_qty
            ELSE 0
        END
    ) AS ventes_meuble,
    SUM(
        CASE
            WHEN pn.product_type = 'DECO' THEN t.prod_price * t.prod_qty
            ELSE 0
        END
    ) AS ventes_deco
FROM
    `test_sevrier.TRANSACTIONS` AS t
LEFT JOIN `test_sevrier.PRODUCT_NOMENCLATURE` AS pn ON t.prod_id = pn.product_id
WHERE
    t.date BETWEEN "2019-01-01" AND "2019-12-31"
GROUP BY
    client_id
```